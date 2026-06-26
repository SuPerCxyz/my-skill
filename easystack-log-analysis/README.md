# EasyStack Log Analysis

EasyStack OpenStack 集群日志(`.eslog`)解压、目录映射、跨服务跨节点根因定位。范围限定为离线 eslog/ecs 目录分析, 不替代运行中环境 SSH/kubectl 排查、仓库 CI 修复或 Web UI E2E。

## 功能

- 加密 `.eslog` 压缩包解压
- 容器化日志目录结构与组件映射
- 跨域关联分析(云主机生命周期 / 云盘挂载卸载 / 网络 / 镜像 / 裸金属 Ironic)
- 强制关联 OS 系统层(内核 / OVS·OVN / SCSI·multipath / IPMI)与控制面基础设施(Galera / RabbitMQ / chrony / Ceph)
- 统一分析报告模板与实战 case

## 快速开始

```bash
# 解压当前目录下所有 .eslog(一次性)
# 后续按 search-patterns.md / troubleshooting.md 中的模式检索根因
```

## 文件说明

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | Skill 主入口，工作流与快速参考 |
| [analysis-playbook.md](analysis-playbook.md) | 标准端到端分析流程 + 报告模板 |
| [cross-domain-analysis.md](cross-domain-analysis.md) | 跨域关联分析矩阵(各场景必看哪些日志) |
| [decompress.md](decompress.md) | eslog 解压方法 |
| [log-format.md](log-format.md) | 日志行格式、字段、awk 配方 |
| [directory-map.md](directory-map.md) | 日志目录结构映射 |
| [search-patterns.md](search-patterns.md) | 按问题类型的搜索模式 |
| [troubleshooting.md](troubleshooting.md) | 故障排查场景与实战 case |
