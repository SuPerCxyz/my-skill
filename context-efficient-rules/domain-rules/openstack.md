# OpenStack 精简规则

## 硬规则

1. **CLI 输出截断**
   - 所有 `openstack` CLI 命令必须 `| head -100`
   - list 命令加 `--limit 50` 或 `-c` 指定关键列
   - 禁止 `openstack server list` 不带 `--limit`

2. **定向查询**
   - 优先使用 `--column` / `-c` 只取需要的字段
   - 优先使用 `--name` / `--id` 精确查，不用 list 全量再 grep
   - `openstack server show <id> -f json` 比默认 table 输出更省 token

3. **日志与服务**
   - 容器日志用 `kubectl logs` 规则（同 K8s 规则）
   - 服务状态查 `openstack compute service list --status down` 先查异常
   - 禁止 `openstack catalog list` 全量 — 按 service type 查

4. **操作防护**
   - delete / evacuate / migrate 操作前必须确认目标
   - 禁止批量操作不带 `--dry-run` 或确认
   - Nova / Cinder 维护操作先查 host state

## 常用安全命令模板

```bash
# 查看 server 列表（精简）
openstack server list --status ACTIVE --limit 20 -c ID -c Name -c Status | head -30

# 查看单个 server 详情（JSON 格式，省 token）
openstack server show <id> -f json | head -60

# 查看异常服务
openstack compute service list --status down | head -20

# 查看网络端口（定向）
openstack port list --server <id> -c ID -c IP -c Status | head -20

# 查看 volume 状态
openstack volume list --status error --limit 20 -c ID -c Name -c Status | head -20
```

## 禁止清单

| 禁止命令 | 替代方案 |
|----------|----------|
| `openstack server list` (无 limit) | `openstack server list --limit 50` |
| `openstack server list --all-projects` | 限定 `--project` |
| `openstack catalog list` | `openstack catalog show <service>` |
| `openstack flavor list -f json` (全量) | `openstack flavor list -c Name -c VCPUs -c RAM` |
| `openstack endpoint list` (无过滤) | `openstack endpoint list --service <type>` |
