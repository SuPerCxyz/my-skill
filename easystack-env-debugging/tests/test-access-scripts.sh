#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
test_root=$(mktemp -d /tmp/easystack-env-access-test.XXXXXX)
trap 'rm -rf -- "$test_root"' EXIT
fake_bin=$test_root/bin
mkdir -p "$fake_bin"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  local file=$1 expected=$2
  grep -F -- "$expected" "$file" >/dev/null || fail "$file missing: $expected"
}

assert_contains "$skill_dir/SKILL.md" \
  "第一项环境相关命令 MUST 直接调用"
assert_contains "$skill_dir/SKILL.md" \
  "不要先读取组件参考文档"
assert_contains "$skill_dir/access.md" \
  'env-access.sh` 会通过'

"$skill_dir/scripts/env-access.sh" --help >"$test_root/env-help"
assert_contains "$test_root/env-help" "Usage:"

set +e
"$skill_dir/scripts/env-access.sh" --env invalid >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "invalid env returned $rc"
assert_contains "$test_root/err" "unsupported --env value"

cat >"$fake_bin/timeout" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >>"$ACCESS_TEST_LOG"
cat >/dev/null
exit "${ACCESS_TIMEOUT_RC:-0}"
EOF
chmod +x "$fake_bin/timeout"

ACCESS_TEST_LOG=$test_root/timeout.log PATH="$fake_bin:$PATH" \
  "$skill_dir/scripts/env-access.sh" --target 192.0.2.10 --mode ssh \
  --no-root --timeout 1 -- hostname
assert_contains "$test_root/timeout.log" "root@192.0.2.10"

: >"$test_root/timeout.log"
set +e
ACCESS_TEST_LOG=$test_root/timeout.log ACCESS_TIMEOUT_RC=124 PATH="$fake_bin:$PATH" \
  "$skill_dir/scripts/env-access.sh" --target 192.0.2.10 --mode ssh \
  --no-root -- "openstack server delete test"
rc=$?
set -e
[[ $rc -eq 124 ]] || fail "destructive timeout returned $rc"
[[ $(wc -l <"$test_root/timeout.log") -eq 1 ]] ||
  fail "destructive command was retried"

"$skill_dir/scripts/jumpserver-env.sh" --help >"$test_root/js-help"
assert_contains "$test_root/js-help" "Usage:"

set +e
"$skill_dir/scripts/jumpserver-env.sh" --asset node --jumpserver-host host \
  >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "partial JumpServer override returned $rc"
assert_contains "$test_root/err" "jumpserver overrides require"

cat >"$fake_bin/expect" <<'EOF'
#!/usr/bin/env bash
printf '%s|%s|%s\n' "$JS_ASSET_QUERY" "$JS_REMOTE_CMD" "$JS_BECOME_ROOT" \
  >"$ACCESS_TEST_LOG"
cat >/dev/null
EOF
chmod +x "$fake_bin/expect"
touch "$test_root/id"
ACCESS_TEST_LOG=$test_root/expect.log PATH="$fake_bin:$PATH" \
  "$skill_dir/scripts/jumpserver-env.sh" --asset node --cmd hostname --no-root \
  --jumpserver-host host --jumpserver-user user --jumpserver-port 2222 \
  --jumpserver-identity-file "$test_root/id" --timeout 1
assert_contains "$test_root/expect.log" "node|hostname|0"

echo "PASS: env-access.sh and jumpserver-env.sh"
