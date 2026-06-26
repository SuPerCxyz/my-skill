# Log Line Format

Use this file when parsing log lines, grouping by node/pod/container, or writing awk/grep pipelines against decompressed `.log` files.

## Wrapper Format (5-field, `¦`-delimited)

All decompressed `.log` files use a uniform 5-field prefix added by the log
collector, separated by a single Unicode middle-bar character `¦` (U+00A6,
NOT the ASCII pipe `|`):

```
<wrapper_ts> +0800 ¦ <node> ¦ <pod_or_source> ¦ <container> ¦ <raw_log_line>
```

Example (from `openstack/nova/nova-compute.node-1.20260618.log`):

```
2026-06-18 10:24:24.517 +0800 ¦ node-1 ¦ nova-compute-67lgd ¦ nova-compute ¦ 2026-06-18T10:24:24.517915479+08:00 stderr F ++ hostname -s
```

Fields:

| # | Field | Notes |
|---|-------|-------|
| 1 | `wrapper_ts` | Collector timestamp (wall clock when the line was harvested) |
| 2 | `node` | Hostname (e.g. `node-1`) |
| 3 | `pod_or_source` | Kubernetes pod name, or `messages` / `bash-history` etc. for OS-level sources |
| 4 | `container` | Container name inside the pod (may be empty for OS sources) |
| 5 | `raw_log_line` | The actual log line emitted by the service |

The application's own timestamp lives **inside** field 5 (e.g.
`2026-06-18T10:24:24.517915479+08:00 stderr F ...`), so a regex on
"date" matches twice per line — the wrapper TS and the inner TS.

## Practical Implications

### Plain grep still works

Plain `grep "VolumeDeviceNotFound" nova-compute.*.log` works because the
text inside field 5 is unchanged. **You do not need to parse the wrapper to
do content search.**

### Use awk when you need pod/container/host axes

```bash
# Count events per pod
awk -F' ¦ ' '/ERROR/ {print $3}' openstack/nova/nova-compute.*.log | sort | uniq -c

# Extract only the raw log line (drop wrapper)
awk -F' ¦ ' '{print $5}' openstack/nova/nova-compute.*.log

# Filter by container name (multi-container pods)
awk -F' ¦ ' '$4 == "nova-compute" {print}' openstack/nova/nova-compute.*.log

# Wrapper TS + raw line only (for clean correlation)
awk -F' ¦ ' '{print $1, $5}' openstack/nova/nova-compute.*.log
```

### Pod restarts show up as pod-name changes

Pods get a new name (`nova-compute-67lgd` → `nova-compute-xyz12`) when they
restart. Track pod restarts by:

```bash
awk -F' ¦ ' '{print $3}' openstack/nova/nova-compute.*.log | sort -u
```

If multiple pod names appear in the same file, the pod was restarted during
the log collection window.

### Time-window filtering

The wrapper TS (field 1) is always `YYYY-MM-DD HH:MM:SS.mmm +0800` and
collator-monotonic. The inner application TS may differ slightly. Filter on
the wrapper TS for reliable time-range search:

```bash
grep "^2026-06-18 10:2[5-9]:" openstack/nova/nova-compute.*.log
```

### OS-level sources have a different inner shape

For `os/messages.*.log`, `os/chrony.*.log`, `openstack/dozer/bash-history.*.log`,
field 4 (container) is empty and field 5 contains the classic syslog line:

```
2026-06-18 10:23:27.000 +0800 ¦ node-1 ¦ messages ¦  ¦ Jun 18 10:23:27 node-1 kubelet[9241]: E0618 10:23:27.448026 ...
```

## Filename Convention

```
<service>.<node>.<date>.log[.gz]
```

The hostname appears both in the directory name (`ecs.node-1.20260618.0/`)
and the filename. `.0` suffix on the directory is the rollover index when
multiple collections are made the same day.

## eslog Filename Time Window

```
ecs.<start_ts>-<end_ts>.eslog
ecs.20260618-20260623183823.eslog
       │                  │
       │                  └── 2026-06-23 18:38:23 collection end
       └── 2026-06-18 collection start (no time = 00:00:00)
```

Read this **first** to know what time range the bundle covers and to
narrow your search.
