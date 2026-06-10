# 日志分析精简规则

## 硬规则

1. **禁止读取完整日志文件**
   - 绝对禁止 `cat /var/log/xxx.log` 或 `Read` 完整日志
   - 日志文件可能数万行，会立即撑爆上下文

2. **grep 先行**
   - 必须先 `grep` / `rg` 定位关键行，再读取上下文
   - 搜索关键词优先级：ERROR > WARN > Exception > 具体错误信息
   - 结果超过 30 行时，加更精确的过滤条件

3. **tail 限制**
   - `tail` 必须指定行数，默认 `-n 100`
   - `tail -f` 禁止在工具中使用（会挂起）
   - 用 `tail -n 200 | grep` 代替持续监控

4. **多日志源策略**
   - 先确定时间范围，按时间过滤
   - 先查错误最多的日志源，不要逐个查所有文件
   - journalctl 用 `--since` / `--until` 限制范围

## 常用安全命令模板

```bash
# 搜索错误（限制结果数）
grep -n "ERROR\|Exception\|Traceback" /var/log/app.log | tail -30

# 查看最近日志
tail -n 100 /var/log/app.log | grep -iE 'error|warn|fail'

# journalctl 限定时间和单元
journalctl -u nova-compute --since "1 hour ago" --no-pager | tail -100

# 搜索特定请求的上下文（先定位行号，再取上下文）
grep -n "request-id" /var/log/app.log | tail -5
# 然后: sed -n '<line-5>,<line+10>p' /var/log/app.log

# 统计错误频率（不输出所有行）
grep -c "ERROR" /var/log/app.log

# 查看日志文件大小（避免读大文件）
ls -lh /var/log/app.log
```

## 分步排查流程

```
1. 确认日志文件位置与大小
   └─ ls -lh /var/log/xxx.log

2. 统计错误数量
   └─ grep -c "ERROR" /var/log/xxx.log

3. 取最近错误（带行号）
   └─ grep -n "ERROR" /var/log/xxx.log | tail -10

4. 取单个错误的上下文（±10 行）
   └─ sed -n '<line-10>,<line+10>p' /var/log/xxx.log

5. 如需关联日志，用时间戳 / request-id 交叉查
```

## 禁止清单

| 禁止命令 | 替代方案 |
|----------|----------|
| `cat /var/log/xxx.log` | `grep` 或 `tail -n 100` |
| `Read /var/log/xxx.log` (全文件) | `Read` 指定 offset/limit ≤ 200 |
| `tail -f` (持续监控) | `tail -n 100` 单次截取 |
| `grep` 不加限制 (可能匹配数万行) | `grep \| tail -30` |
| `less` / `more` (交互式) | `sed -n 'start,end p'` |
