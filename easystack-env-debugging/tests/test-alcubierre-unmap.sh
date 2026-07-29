#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
script=$skill_dir/scripts/alcubierre-unmap.sh
mapping_helper=$skill_dir/scripts/alcubierre-mapping.sh
runner=$skill_dir/scripts/run-alcubierre-unmap.sh
test_root=$(mktemp -d /tmp/alcubierre-unmap-test.XXXXXX)
trap 'rm -rf -- "$test_root"' EXIT
fake_bin=$test_root/bin
marker=$test_root/disconnected
volume_call_log=$test_root/volume-calls
mapping_call_log=$test_root/mapping-calls
mkdir -p "$fake_bin"
export ALCUB_TEST_VOLUME_CALL_LOG=$volume_call_log
export ALCUB_TEST_MAPPING_CALL_LOG=$mapping_call_log

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  local file=$1 expected=$2
  if ! grep -F -- "$expected" "$file" >/dev/null; then
    sed -n '1,80p' "$file" >&2
    fail "$file missing: $expected"
  fi
}

assert_matches() {
  local file=$1 pattern=$2
  grep -Eq -- "$pattern" "$file" ||
    fail "$file missing pattern: $pattern"
}

volume_call_count() {
  if [[ -f "$volume_call_log" ]]; then
    wc -l <"$volume_call_log"
  else
    echo 0
  fi
}

assert_volume_call_delta() {
  local before=$1 expected=$2 description=$3
  local after

  after=$(volume_call_count)
  [[ $((after - before)) -eq "$expected" ]] ||
    fail "$description used $((after - before)) volume scans, expected $expected"
}

mapping_call_count() {
  if [[ -f "$mapping_call_log" ]]; then
    wc -l <"$mapping_call_log"
  else
    echo 0
  fi
}

assert_mapping_call_delta() {
  local before=$1 expected=$2 description=$3
  local after

  after=$(mapping_call_count)
  [[ $((after - before)) -eq "$expected" ]] ||
    fail "$description used $((after - before)) mapping batches, expected $expected"
}

uuid_no_mapping=134859be-a9f3-4213-ba6b-2805755ad79d
uuid_mapped=17baef6b-c018-485c-b19c-38be83ff9c6f
uuid_nvme=2706a1db-bad0-4846-9595-fc8287108f40

cat >"$fake_bin/kubectl" <<'EOF'
#!/usr/bin/env bash
set -eu
args="$*"

if [[ "$args" == *"get pod"* ]]; then
  echo "manul-healthy 1/1 Running 0 1h"
elif [[ "$args" == *"kvctl list volume --format"* ]]; then
  printf 'called\n' >>"$ALCUB_TEST_VOLUME_CALL_LOG"
  echo "Volume(name='volume-134859be-a9f3-4213-ba6b-2805755ad79d', id='alcub_disk1', state=<State.LINKED: 'linked'>, task_state=<TaskState.IDLE: 'idle'>, error_message='', protocol='ISCSI')"
  if [[ -f "$ALCUB_TEST_MARKER" &&
        "${ALCUB_TEST_FINAL_BAD_STATE:-0}" == "1" ]]; then
    echo "Volume(name='volume-17baef6b-c018-485c-b19c-38be83ff9c6f', id='alcub_disk2', state=<State.LINKED: 'linked'>, task_state=<TaskState.IDLE: 'idle'>, error_message='stuck', protocol='ISCSI')"
  elif [[ -f "$ALCUB_TEST_MARKER" ]]; then
    echo "Volume(name='volume-17baef6b-c018-485c-b19c-38be83ff9c6f', id='alcub_disk2', state=<State.UNLINKED: 'unlinked'>, task_state=<TaskState.CACHE_DELETE_WAITING: 'cache_delete_waiting'>, error_message='', protocol='ISCSI')"
  else
    echo "Volume(name='volume-17baef6b-c018-485c-b19c-38be83ff9c6f', id='alcub_disk2', state=<State.LINKED: 'linked'>, task_state=<TaskState.IDLE: 'idle'>, error_message='', protocol='ISCSI')"
  fi
  echo "Volume(name='volume-2706a1db-bad0-4846-9595-fc8287108f40', id='alcub_disk3', state=<State.LINKED: 'linked'>, task_state=<TaskState.IDLE: 'idle'>, error_message='', protocol='NVMEOF')"
elif [[ "$args" == *"__ALCUB_MAPPING_BEGIN__"* ]]; then
  printf 'called\n' >>"$ALCUB_TEST_MAPPING_CALL_LOG"
  while [[ $# -gt 0 && "$1" != "--targets" ]]; do shift; done
  [[ $# -gt 0 ]] && shift
  while [[ $# -ge 2 ]]; do
    protocol=$1
    disk=$2
    shift 2
    echo "__ALCUB_MAPPING_BEGIN__|$protocol|$disk"
    if [[ "$disk" == "alcub_disk2" && ! -f "$ALCUB_TEST_MARKER" ]]; then
      printf '%s\n' \
        '{"hostname": "node-2", "initiator": "iqn.test"}' \
        '{"hostname": "node-3", "initiator": "iqn.test"}'
    elif [[ "$disk" == "alcub_disk3" ]]; then
      printf '%s\n' \
        '{"hostname": "node-2", "hostnqn": "nqn.test"}' \
        '{"hostname": "node-3", "hostnqn": "nqn.test"}'
    fi
    echo "__ALCUB_MAPPING_END__|$protocol|$disk|0"
  done
else
  echo "unexpected kubectl invocation: $args" >&2
  exit 2
fi
EOF
chmod +x "$fake_bin/kubectl"

cat >"$fake_bin/curl" <<'EOF'
#!/usr/bin/env bash
[[ "$*" == *"alcub_disk2/disconnections"* ]] || exit 3
printf 'called\n' >>"$ALCUB_TEST_MARKER"
[[ "${ALCUB_TEST_FAIL_AFTER_DISCONNECT:-0}" != "1" ]] || exit 28
EOF
chmod +x "$fake_bin/curl"

test -f "$script" || fail "missing $script"
test -f "$mapping_helper" || fail "missing $mapping_helper"
test -f "$runner" || fail "missing $runner"

calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
ALCUB_TEST_MARKER=$marker PATH="$fake_bin:$PATH" \
  bash "$script" --remote preflight \
  "$uuid_mapped" "$uuid_mapped" "$uuid_nvme" \
  >"$test_root/preflight"
assert_volume_call_delta "$calls_before" 1 "preflight"
assert_mapping_call_delta "$mapping_before" 1 "preflight"
assert_contains "$test_root/preflight" \
  "MAP_COUNT=2|CLIENT_COUNT=1|CLIENTS=iqn.test"
assert_contains "$test_root/preflight" \
  "PREFLIGHT|$uuid_nvme|DISK_ID=alcub_disk3|PROTOCOL=NVMEOF"
assert_contains "$test_root/preflight" "CLIENTS=nqn.test|RESULT=READY"
assert_contains "$test_root/preflight" "RESULT=READY"
assert_matches "$test_root/preflight" \
  '^TIMING[|]PHASE=INITIAL_VOLUME[|]SECONDS=[0-9]+$'
assert_matches "$test_root/preflight" \
  '^TIMING[|]PHASE=INITIAL_MAPPING[|]SECONDS=[0-9]+$'
assert_matches "$test_root/preflight" \
  '^TIMING[|]PHASE=TOTAL[|]SECONDS=[0-9]+$'
[[ $(grep -c "^PREFLIGHT|$uuid_mapped|" "$test_root/preflight") -eq 1 ]] ||
  fail "duplicate UUID was not removed"

resume_marker=$test_root/resume-disconnected
calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
set +e
ALCUB_TEST_MARKER=$resume_marker ALCUB_TEST_FAIL_AFTER_DISCONNECT=1 \
PATH="$fake_bin:$PATH" \
  bash "$script" --remote execute "$uuid_mapped" \
  >"$test_root/interrupted"
rc=$?
set -e
[[ $rc -eq 23 ]] || fail "unknown API result returned $rc"
assert_volume_call_delta "$calls_before" 1 "failed execute"
assert_mapping_call_delta "$mapping_before" 1 "failed execute"
assert_contains "$test_root/interrupted" "FAILED_API|$uuid_mapped"
assert_matches "$test_root/interrupted" \
  "^TIMING[|]PHASE=API[|]VOLUME_ID=$uuid_mapped[|]SECONDS=[0-9]+$"

calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
ALCUB_TEST_MARKER=$resume_marker PATH="$fake_bin:$PATH" \
  bash "$script" --remote execute "$uuid_mapped" \
  >"$test_root/interrupted-resume"
assert_volume_call_delta "$calls_before" 2 "resumed execute"
assert_mapping_call_delta "$mapping_before" 2 "resumed execute"
assert_contains "$test_root/interrupted-resume" \
  "SUCCESS_NOOP|$uuid_mapped|MAPPING=0|STATE=UNLINKED"
[[ $(wc -l <"$resume_marker") -eq 1 ]] ||
  fail "resume repeated API after unknown result"

calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
ALCUB_TEST_MARKER=$marker PATH="$fake_bin:$PATH" \
  bash "$script" --remote execute "$uuid_no_mapping" "$uuid_mapped" \
  >"$test_root/execute"
assert_volume_call_delta "$calls_before" 2 "batch execute"
assert_mapping_call_delta "$mapping_before" 2 "batch execute"
assert_contains "$test_root/execute" \
  "SUCCESS_NOOP|$uuid_no_mapping|MAPPING=0|STATE=LINKED"
assert_contains "$test_root/execute" \
  "MAPPING_CLEARED|$uuid_mapped|MAPPING=0"
assert_matches "$test_root/execute" \
  '^TIMING[|]PHASE=API_TOTAL[|]SECONDS=[0-9]+$'
assert_matches "$test_root/execute" \
  '^TIMING[|]PHASE=FINAL_MAPPING[|]SECONDS=[0-9]+$'
assert_matches "$test_root/execute" \
  '^TIMING[|]PHASE=FINAL_VOLUME[|]SECONDS=[0-9]+$'
[[ $(wc -l <"$marker") -eq 1 ]] ||
  fail "disconnection API was not called exactly once"

calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
ALCUB_TEST_MARKER=$marker PATH="$fake_bin:$PATH" \
  bash "$script" --remote execute "$uuid_no_mapping" "$uuid_mapped" \
  >"$test_root/resume"
assert_volume_call_delta "$calls_before" 2 "noop execute"
assert_mapping_call_delta "$mapping_before" 2 "noop execute"
assert_contains "$test_root/resume" \
  "SUCCESS_NOOP|$uuid_no_mapping|MAPPING=0|STATE=LINKED"
assert_contains "$test_root/resume" \
  "SUCCESS_NOOP|$uuid_mapped|MAPPING=0|STATE=UNLINKED"
[[ $(wc -l <"$marker") -eq 1 ]] ||
  fail "resume repeated the disconnection API"

calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
ALCUB_TEST_MARKER=$marker PATH="$fake_bin:$PATH" \
  bash "$script" --remote verify "$uuid_no_mapping" "$uuid_mapped" \
  >"$test_root/verify"
assert_volume_call_delta "$calls_before" 1 "verify"
assert_mapping_call_delta "$mapping_before" 1 "verify"
assert_contains "$test_root/verify" \
  "VERIFY|$uuid_mapped|PROTOCOL=ISCSI|MAPPING=0|STATE=UNLINKED"

bad_state_marker=$test_root/bad-state-disconnected
calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
set +e
ALCUB_TEST_MARKER=$bad_state_marker ALCUB_TEST_FINAL_BAD_STATE=1 \
PATH="$fake_bin:$PATH" \
  bash "$script" --remote execute "$uuid_mapped" \
  >"$test_root/bad-state"
rc=$?
set -e
[[ $rc -eq 1 ]] || fail "final bad volume state returned $rc"
assert_volume_call_delta "$calls_before" 2 "bad-state execute"
assert_mapping_call_delta "$mapping_before" 2 "bad-state execute"
assert_contains "$test_root/bad-state" \
  "VERIFY|$uuid_mapped|PROTOCOL=ISCSI|MAPPING=0|STATE=LINKED"
assert_contains "$test_root/bad-state" "ERROR=stuck|RESULT=FAILED"

set +e
PATH="$fake_bin:$PATH" \
  bash "$script" --remote preflight invalid-uuid \
  >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "invalid UUID returned $rc"
assert_contains "$test_root/err" "invalid volume UUID"

cat >"$test_root/fake-env-access" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$@" >"$ALCUB_ACCESS_LOG"
while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--cmd" ]]; then
    shift
    [[ "${ALCUB_RUN_REMOTE:-0}" != "1" ]] || bash -c "$1"
    break
  fi
  shift
done
EOF
chmod +x "$test_root/fake-env-access"

calls_before=$(volume_call_count)
mapping_before=$(mapping_call_count)
ALCUB_ACCESS_LOG=$test_root/access.log ALCUB_RUN_REMOTE=1 \
ALCUB_TEST_MARKER=$marker PATH="$fake_bin:$PATH" \
EASYSTACK_ENV_ACCESS_SCRIPT=$test_root/fake-env-access \
  bash "$runner" --via eswork --target 192.168.3.3 -- \
  preflight "$uuid_nvme" >"$test_root/runner-preflight"
assert_volume_call_delta "$calls_before" 1 "bundled runner"
assert_mapping_call_delta "$mapping_before" 1 "bundled runner"
assert_contains "$test_root/access.log" "--via"
assert_contains "$test_root/access.log" "--cmd"
assert_contains "$test_root/access.log" "--timeout"
assert_contains "$test_root/runner-preflight" "PROTOCOL=NVMEOF"

echo "PASS: alcubierre-unmap.sh"
