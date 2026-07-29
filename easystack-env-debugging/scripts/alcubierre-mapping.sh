#!/usr/bin/env bash

refresh_mapping_snapshot() {
  local volume_id
  local -a targets=()

  for volume_id in "${volume_ids[@]}"; do
    query_volume "$volume_id" || continue
    [[ "$protocol" == "ISCSI" || "$protocol" == "NVMEOF" ]] &&
      targets+=("$protocol" "$disk_id")
  done
  [[ ${#targets[@]} -gt 0 ]] || {
    mapping_snapshot=""
    return
  }
  mapping_snapshot=$(kubectl exec -n alcubierre "$manul_pod" -c manul -- \
    bash -c '
      set +e
      [[ "${1:-}" == "--targets" ]] || exit 2
      shift
      while [[ $# -ge 2 ]]; do
        protocol=$1; disk=$2; shift 2
        printf "__ALCUB_MAPPING_BEGIN__|%s|%s\n" "$protocol" "$disk"
        if [[ "$protocol" == "ISCSI" ]]; then
          output=$(kvctl list volumemapping --where "name=$disk" 2>&1)
        else
          output=$(kvctl list nvmemapping --where "volume_id=$disk" 2>&1)
        fi
        rc=$?
        printf "%s\n" "$output"
        printf "__ALCUB_MAPPING_END__|%s|%s|%s\n" \
          "$protocol" "$disk" "$rc"
      done
    ' -- --targets "${targets[@]}")
}

query_mapping() {
  local client_field client_lines begin end status

  case "$protocol" in
    ISCSI) client_field="initiator" ;;
    NVMEOF) client_field="hostnqn" ;;
    *) return 2 ;;
  esac
  begin="__ALCUB_MAPPING_BEGIN__|$protocol|$disk_id"
  end="__ALCUB_MAPPING_END__|$protocol|$disk_id|"
  mapping_output=$(printf '%s\n' "$mapping_snapshot" |
    awk -v begin="$begin" -v end="$end" '
      $0 == begin { capture=1; next }
      index($0, end) == 1 { capture=0; next }
      capture { print }
    ')
  status=$(printf '%s\n' "$mapping_snapshot" |
    grep -F -- "$end" | sed -n 's/.*|//p')
  [[ "$status" == "0" ]] || return 3

  client_lines=$(printf '%s\n' "$mapping_output" |
    grep -oE "\"${client_field}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" |
    awk -F'"' '{print $4}' || true)
  map_count=$(printf '%s\n' "$client_lines" | sed '/^$/d' | wc -l)
  clients=$(printf '%s\n' "$client_lines" |
    sed '/^$/d' | sort -u | paste -sd, -)
  client_count=$(printf '%s\n' "$clients" |
    tr ',' '\n' | sed '/^$/d' | wc -l)

  if [[ "$map_count" == "0" &&
        ("$client_count" != "0" || -n "$clients") ]]; then
    echo "mapping parser returned inconsistent results for $disk_id" >&2
    return 4
  fi
}
