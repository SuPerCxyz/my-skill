# EasyStack Log Analysis

EasyStack OpenStack 集群日志(`.eslog`)安全解压、目录映射、跨服务跨节点根因定位。
历史故障同时需要运行中环境检查时, 与 `easystack-env-debugging` 联合使用并输出相同的
无表格、行首安全问题分析结论。

## 功能

- 加密 `.eslog` 压缩包解压
- 容器化日志目录结构与组件映射
- 跨域关联分析(云主机生命周期 / 云盘挂载卸载 / 网络 / 镜像 / 裸金属 Ironic)
- 强制关联 OS 系统层(内核 / OVS·OVN / SCSI·multipath / IPMI)与控制面基础设施(Galera / RabbitMQ / chrony / Ceph)
- 与 env-debugging 同步的行首安全、无表格分析报告模板与实战 case

## 快速开始

```bash
# Explicit input and output
bash scripts/decompress-eslog.sh --input /path/to/bundle.eslog --output /path/to/output

# Default: all top-level .eslog files in the current directory
bash scripts/decompress-eslog.sh
```

默认保留 `.log.gz` 以控制磁盘占用; 只有确认空间充足时才使用 `--decompress-logs`。

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口,工作流与快速参考 |
| [analysis-playbook.md](analysis-playbook.md) | 标准端到端分析流程 + 报告模板 |
| [report-format.md](report-format.md) | 与 env-debugging 同步且含一句话总结的结论格式 |
| [cross-domain-analysis.md](cross-domain-analysis.md) | 跨域关联分析矩阵(各场景必看哪些日志) |
| [decompress.md](decompress.md) | eslog 解压方法 |
| [scripts/decompress-eslog.sh](scripts/decompress-eslog.sh) | 安全解压脚本 |
| [log-format.md](log-format.md) | 日志行格式、字段、awk 配方 |
| [directory-map.md](directory-map.md) | 日志目录结构映射 |
| [search-patterns.md](search-patterns.md) | 按问题类型的搜索模式 |
| [troubleshooting.md](troubleshooting.md) | 故障排查场景与实战 case |
