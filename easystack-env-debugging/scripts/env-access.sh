#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  env-access.sh --target <TARGET> [--mode auto|ssh|jump18|jumpserver] [-- CMD...]
  env-access.sh --env <BJ_ENV> [-- CMD...]
  env-access.sh --asset <ASSET_NAME> --mode jumpserver [-- CMD...]
  env-access.sh --target <TARGET> --cmd 'kubectl get nodes -o name'

Examples:
  env-access.sh --env BJ-<ENV_ID>
  env-access.sh --env BJ-<ENV_ID> -- whoami
  env-access.sh --target 172.<ENV_ID>.0.2 -- kubectl get nodes -o name
  env-access.sh --target 172.18.0.118 --control-node 10.20.0.3 -- hostname
  env-access.sh --asset <ASSET_NAME> --mode jumpserver -- whoami

Options:
  --target TARGET       SSH target, IP, alias, or BJ-xx name.
  --env NAME            Environment name, such as BJ-<ENV_ID>. Converts to 172.<ENV_ID>.0.2.
  --asset NAME          JumpServer asset name for menu fallback.
  --mode MODE           auto, ssh, jump18, or jumpserver. Default: auto.
  --cmd COMMAND         Command string to run after login.
  --control-node IP     Inner control node for 172.18.* jump host mode. Default: 10.20.0.3.
  --alias NAME          SSH config alias for JumpServer menu mode. Default: js.
  --asset-id ID         Asset ID for JumpServer menu mode.
  --timeout SECONDS     Timeout for JumpServer menu mode.
  --no-root             Do not run sudo/root shell after login.
  -h, --help            Show this help.

Without CMD or --cmd, opens an interactive shell.
EOF
}

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mode="auto"
target=""
env_name=""
asset_name=""
asset_id=""
remote_cmd=""
control_node="10.20.0.3"
jumpserver_alias="js"
single_timeout=""
become_root="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      target="${2:?missing value for --target}"
      shift 2
      ;;
    --env)
      env_name="${2:?missing value for --env}"
      shift 2
      ;;
    --asset)
      asset_name="${2:?missing value for --asset}"
      shift 2
      ;;
    --mode)
      mode="${2:?missing value for --mode}"
      shift 2
      ;;
    --cmd)
      remote_cmd="${2:?missing value for --cmd}"
      shift 2
      ;;
    --control-node)
      control_node="${2:?missing value for --control-node}"
      shift 2
      ;;
    --alias)
      jumpserver_alias="${2:?missing value for --alias}"
      shift 2
      ;;
    --asset-id)
      asset_id="${2:?missing value for --asset-id}"
      shift 2
      ;;
    --timeout)
      single_timeout="${2:?missing value for --timeout}"
      shift 2
      ;;
    --no-root)
      become_root="0"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      remote_cmd="$*"
      break
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

target_from_env() {
  local value="$1"
  if [[ "$value" =~ ^[Bb][Jj]-?([0-9]+)$ ]]; then
    printf '172.%s.0.2\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

if [[ -z "$target" && -n "$env_name" ]]; then
  if ! target="$(target_from_env "$env_name")"; then
    echo "unsupported --env value: $env_name" >&2
    exit 2
  fi
  if [[ -z "$asset_name" ]]; then
    asset_name="$env_name"
  fi
fi

if [[ -n "$target" ]]; then
  if converted="$(target_from_env "$target")"; then
    target="$converted"
  fi
fi

detect_mode() {
  if [[ -n "$target" && "$target" == 172.18.* ]]; then
    printf 'jump18\n'
  elif [[ -n "$target" ]]; then
    printf 'ssh\n'
  elif [[ -n "$asset_name" ]]; then
    printf 'jumpserver\n'
  else
    echo "missing --target, --env, or --asset" >&2
    exit 2
  fi
}

requested_mode="$mode"

if [[ "$mode" == "auto" ]]; then
  mode="$(detect_mode)"
fi

ssh_destination() {
  if [[ "$target" == *@* ]]; then
    printf '%s\n' "$target"
  elif [[ "$target" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ && ! "$target" =~ ^172\.[0-9]+\.0\.2$ ]]; then
    printf 'root@%s\n' "$target"
  else
    printf '%s\n' "$target"
  fi
}

target_uses_interactive_ssh_config() {
  [[ "$target" =~ ^172\.[0-9]+\.0\.2$ ]]
}

run_ssh_config_expect() {
  local timeout_value="${single_timeout:-60}"

  SSH_TARGET="$target" \
  SSH_REMOTE_CMD="$remote_cmd" \
  SSH_BECOME_ROOT="$become_root" \
  SSH_TIMEOUT="$timeout_value" \
  expect <<'EXPECT'
set timeout $env(SSH_TIMEOUT)
set target $env(SSH_TARGET)
set remote_cmd $env(SSH_REMOTE_CMD)
set become_root $env(SSH_BECOME_ROOT)
set shell_re {\[[^]]+@[^]]+[[:space:]]+[^]]+\][#$][[:space:]]*$}
set root_re {\[root@[^]]+[[:space:]]+[^]]+\]#[[:space:]]*$}

proc fail {code message} {
    send_user "$message\n"
    exit $code
}

spawn ssh -tt $target

expect {
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    -re {开始连接到|Last login|Authorized users only|复用SSH连接} {
        exp_continue
    }
    -re $shell_re {
        send_user "connected to target asset\n"
    }
    "Permission denied" {
        fail 2 "SSH authentication failed"
    }
    timeout {
        fail 124 "timeout connecting to target asset"
    }
    eof {
        fail 2 "connection closed while connecting to target asset"
    }
}

if {$become_root eq "1"} {
    send "sudo su -\r"
    expect {
        -re $root_re {
            send_user "became root\n"
        }
        "not in the sudoers" {
            fail 2 "sudo permission denied"
        }
        "password" {
            fail 2 "sudo su - requires password"
        }
        timeout {
            send "exit\r"
            fail 124 "timeout becoming root"
        }
        eof {
            fail 2 "connection closed while becoming root"
        }
    }
}

if {$remote_cmd ne ""} {
    send -- "$remote_cmd\r"
    expect {
        -re $shell_re {}
        timeout {
            send "\003"
            send "exit\r"
            fail 124 "timeout waiting for command prompt"
        }
        eof {
            fail 2 "connection closed while running command"
        }
    }
    send "exit\r"
    expect {
        -re $shell_re {
            send "exit\r"
            expect {
                eof {}
                timeout { exit 0 }
            }
        }
        eof {}
        timeout { exit 0 }
    }
    exit 0
}

send "cd ~\r"
interact
EXPECT
}

run_ssh_target() {
  if target_uses_interactive_ssh_config; then
    run_ssh_config_expect
    return
  fi

  local destination
  destination="$(ssh_destination)"
  local destination_is_root="0"
  if [[ "$destination" == root@* ]]; then
    destination_is_root="1"
  fi
  local ssh_opts=(
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=8
  )

  if [[ -n "$remote_cmd" ]]; then
    if [[ "$become_root" == "1" && "$destination_is_root" == "0" ]]; then
      ssh "${ssh_opts[@]}" "$destination" 'sudo -n bash -s' <<<"$remote_cmd"
    else
      ssh "${ssh_opts[@]}" "$destination" 'bash -s' <<<"$remote_cmd"
    fi
  else
    if [[ "$become_root" == "1" && "$destination_is_root" == "0" ]]; then
      ssh -tt "${ssh_opts[@]}" "$destination" 'sudo su -'
    else
      ssh -tt "${ssh_opts[@]}" "$destination"
    fi
  fi
}

run_jump18() {
  local outer=(
    sshpass -p "easystack" ssh
    -F /dev/null
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=8
  )
  local inner=(
    ssh
    -F /dev/null
    -i /root/.ssh/id_rsa.roller
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=5
    "root@$control_node"
  )
  local inner_cmd

  printf -v inner_cmd '%q ' "${inner[@]}"

  if [[ -n "$remote_cmd" ]]; then
    "${outer[@]}" "root@$target" "${inner_cmd} bash -s" <<<"$remote_cmd"
  else
    "${outer[@]}" -tt "root@$target" "${inner_cmd}"
  fi
}

run_jumpserver() {
  local args=(--alias "$jumpserver_alias")

  if [[ -n "$asset_name" ]]; then
    args+=(--asset "$asset_name")
  elif [[ -n "$target" ]]; then
    args+=(--asset "$target")
  else
    echo "jumpserver mode requires --asset or --target" >&2
    exit 2
  fi

  if [[ -n "$asset_id" ]]; then
    args+=(--asset-id "$asset_id")
  fi
  if [[ -n "$single_timeout" ]]; then
    args+=(--timeout "$single_timeout")
  fi
  if [[ "$become_root" == "0" ]]; then
    args+=(--no-root)
  fi
  if [[ -n "$remote_cmd" ]]; then
    args+=(--cmd "$remote_cmd")
  fi

  "$script_dir/jumpserver-env.sh" "${args[@]}"
}

case "$mode" in
  ssh)
    [[ -n "$target" ]] || { echo "ssh mode requires --target or --env" >&2; exit 2; }
    set +e
    run_ssh_target
    ssh_rc=$?
    set -e
    if [[ "$ssh_rc" -eq 0 ]]; then
      exit 0
    fi
    if [[ "$requested_mode" == "auto" && -n "$asset_name" ]]; then
      echo "ssh mode failed, falling back to JumpServer menu for asset: $asset_name" >&2
      run_jumpserver
    else
      exit "$ssh_rc"
    fi
    ;;
  jump18)
    [[ -n "$target" ]] || { echo "jump18 mode requires --target" >&2; exit 2; }
    run_jump18
    ;;
  jumpserver)
    run_jumpserver
    ;;
  *)
    echo "unsupported --mode: $mode" >&2
    usage >&2
    exit 2
    ;;
esac
