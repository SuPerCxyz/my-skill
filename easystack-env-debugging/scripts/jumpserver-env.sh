#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  jumpserver-env.sh --asset <ASSET_NAME> [--alias js]
  jumpserver-env.sh --asset <ASSET_NAME> --cmd 'whoami; id -u; hostname; pwd'

Options:
  --alias NAME       SSH config alias for JumpServer. Default: js
  --asset NAME       JumpServer asset name or search text. Required.
  --query TEXT       JumpServer menu query. Default: same as --asset
  --asset-id ID      Asset ID to select after --query enters [Host]>.
  --cmd COMMAND      Run one command after sudo root, then exit cleanly.
  --timeout SECONDS  Use one timeout instead of retry ladder.
  --no-root          Do not run sudo su - after connecting to the asset.
  -h, --help         Show this help.

Default behavior opens an interactive root shell on the target asset.
EOF
}

jumpserver_alias="js"
asset_name=""
asset_query=""
asset_id=""
remote_cmd=""
single_timeout=""
become_root="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --alias)
      jumpserver_alias="${2:?missing value for --alias}"
      shift 2
      ;;
    --asset)
      asset_name="${2:?missing value for --asset}"
      shift 2
      ;;
    --query)
      asset_query="${2:?missing value for --query}"
      shift 2
      ;;
    --asset-id)
      asset_id="${2:?missing value for --asset-id}"
      shift 2
      ;;
    --cmd)
      remote_cmd="${2:?missing value for --cmd}"
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
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$asset_name" && -z "$asset_query" ]]; then
  echo "missing required --asset or --query" >&2
  usage >&2
  exit 2
fi

if [[ -z "$asset_query" ]]; then
  asset_query="$asset_name"
fi

if [[ -n "$single_timeout" ]]; then
  timeouts=("$single_timeout")
else
  timeouts=(10 15 20 30 45 60)
fi

run_expect() {
  local timeout_value="$1"
  JS_ALIAS="$jumpserver_alias" \
  JS_ASSET_QUERY="$asset_query" \
  JS_ASSET_ID="$asset_id" \
  JS_REMOTE_CMD="$remote_cmd" \
  JS_BECOME_ROOT="$become_root" \
  JS_TIMEOUT="$timeout_value" \
  expect <<'EXPECT'
set timeout $env(JS_TIMEOUT)
set jumpserver_alias $env(JS_ALIAS)
set asset_query $env(JS_ASSET_QUERY)
set asset_id $env(JS_ASSET_ID)
set remote_cmd $env(JS_REMOTE_CMD)
set become_root $env(JS_BECOME_ROOT)
set ssh_config "$env(HOME)/.ssh/config"
set shell_re {\[[^]]+@[^]]+[[:space:]]+[^]]+\][#$][[:space:]]*$}
set root_re {\[root@[^]]+[[:space:]]+[^]]+\]#[[:space:]]*$}
set menu_re {Opt>|\[Host\]>}

proc fail {code message} {
    send_user "$message\n"
    exit $code
}

proc close_from_shell {shell_re menu_re} {
    send "exit\r"
    expect {
        -re $menu_re {
            send "q\r"
            expect {
                eof {}
                timeout { exit 0 }
            }
        }
        -re $shell_re {
            send "exit\r"
            expect {
                -re $menu_re {
                    send "q\r"
                    expect {
                        eof {}
                        timeout { exit 0 }
                    }
                }
                eof {}
                timeout { exit 0 }
            }
        }
        eof {}
        timeout { exit 0 }
    }
}

spawn ssh -tt -F $ssh_config $jumpserver_alias

expect {
    -re $menu_re {
        send_user "entered JumpServer menu\n"
    }
    "Bad owner or permissions" {
        fail 2 "ssh config permissions error"
    }
    "Permission denied" {
        fail 2 "JumpServer SSH authentication failed"
    }
    timeout {
        fail 124 "timeout waiting for JumpServer menu"
    }
    eof {
        fail 2 "JumpServer connection closed before menu"
    }
}

send -- "$asset_query\r"

expect {
    -re {\[Host\]>} {
        if {$asset_id ne ""} {
            send -- "$asset_id\r"
        } else {
            send -- "$asset_query\r"
        }
        exp_continue
    }
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
    timeout {
        send "exit\r"
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
    close_from_shell $shell_re $menu_re
    exit 0
}

send "cd ~\r"
interact
EXPECT
}

last_status=0
for timeout_value in "${timeouts[@]}"; do
  echo "try JumpServer timeout: ${timeout_value}s" >&2
  if run_expect "$timeout_value"; then
    exit 0
  fi
  last_status=$?
  if [[ "$last_status" -ne 124 ]]; then
    exit "$last_status"
  fi
done

exit "$last_status"
