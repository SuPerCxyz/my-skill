# Kubernetes 精简规则

## 硬规则

1. **禁止全量输出**
   - `kubectl get pods` 必须加 `--no-headers -o wide` 或 `-o name`
   - 结果超过 50 行时，用 `| head -50` 截断
   - 禁止 `kubectl get all` — 按资源类型逐个查

2. **禁止 kubectl describe 全量**
   - `kubectl describe` 输出通常 > 200 行，禁止直接执行
   - 替代方案：`kubectl get <resource> <name> -o jsonpath='{.status.conditions}'`
   - 需要 events 时：`kubectl get events --field-selector involvedObject.name=<name> --sort-by=.lastTimestamp | tail -20`

3. **日志限制**
   - `kubectl logs` 必须加 `--tail=100` 或 `--since=5m`
   - 多容器 pod 必须指定 `-c <container>`
   - 日志超过 100 行时，先 `grep -i error|warn|fail` 过滤

4. **kubectl apply 防护**
   - apply 前必须 `kubectl diff` 先预览
   - 禁止 `kubectl delete` 不带 `--dry-run=client` 首次执行
   - 命名空间操作必须显式指定 `-n`，不依赖 current context

## 常用安全命令模板

```bash
# 查看 pod 状态（精简输出）
kubectl get pods -n <ns> -o wide | head -30

# 查看 pod 条件（替代 describe）
kubectl get pod <name> -n <ns> -o jsonpath='{.status.conditions[*]}' | jq .

# 查看最近日志（过滤错误）
kubectl logs <pod> -n <ns> --tail=100 2>&1 | grep -iE 'error|warn|fail|exception' | tail -20

# 查看最近 events
kubectl get events -n <ns> --sort-by=.lastTimestamp | tail -20

# 安全 diff（apply 前）
kubectl diff -f <manifest.yaml> 2>&1 | head -100
```

## 禁止清单

| 禁止命令 | 替代方案 |
|----------|----------|
| `kubectl get all --all-namespaces` | 按 ns、按资源类型查 |
| `kubectl describe pod <name>` | `kubectl get pod <name> -o jsonpath=...` |
| `kubectl logs <pod>` (无 tail) | `kubectl logs <pod> --tail=100` |
| `kubectl delete <resource> --all` | 逐个删除，先 dry-run |
| `kubectl apply -f <dir>/` (无 diff) | 先 `kubectl diff -f <dir>/` |
