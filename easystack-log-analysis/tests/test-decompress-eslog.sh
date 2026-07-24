#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
test_root=$(mktemp -d /tmp/easystack-eslog-test.XXXXXX)
trap 'rm -rf -- "$test_root"' EXIT
fixture=$test_root/fixture
output=$test_root/output
mkdir -p "$fixture/tree/ecs.node-1.20260724.0/openstack/nova"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

log_path=$fixture/tree/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log
printf 'request-id=req-test instance=vm-test\n' >"$log_path"
gzip "$log_path"
tar -cf "$fixture/ecs-node.tar" -C "$fixture/tree" ecs.node-1.20260724.0
mkdir "$fixture/inner"
cp "$fixture/ecs-node.tar" "$fixture/inner/"
(
  cd "$fixture/inner"
  zip -q "$fixture/nested.zip" ecs-node.tar
)
cp "$fixture/nested.zip" "$fixture/sample.eslog.0"
(
  cd "$fixture"
  zip -q "$test_root/sample.eslog" sample.eslog.0
)

bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"

result=$output/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log
[[ -f $result ]] || fail "readable .log was not generated"
grep -F "req-test" "$result" >/dev/null || fail "generated log content mismatch"
[[ -f $result.gz ]] || fail "original .log.gz was not preserved"

printf 'keep\n' >"$output/ecs.node-1.20260724.0/previous-file.txt"
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"
[[ -f $output/ecs.node-1.20260724.0/previous-file.txt ]] ||
  fail "merge removed a file absent from the new bundle"

set +e
bash "$skill_dir/scripts/decompress-eslog.sh" --decompress-logs \
  >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "removed option returned $rc"
grep -F "Unknown argument: --decompress-logs" "$test_root/err" >/dev/null ||
  fail "removed option error was unclear"

echo "PASS: decompress-eslog.sh"
