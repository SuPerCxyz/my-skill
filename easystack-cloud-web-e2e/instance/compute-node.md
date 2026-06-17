# 计算节点（Compute Node）

## 页面信息

| 项目 | 值 |
|------|-----|
| 列表 URL | `https://<IP>/eec/hosts` |
| 导航路径 | Computing → Compute Node |
| 侧边栏定位方式 | `#nova__subsvc_left__phy_host` |

## 页面说明

计算节点是用于管理实例、GPU、USB 等设备的物理服务器。不可创建，只能查看和管理。

## 列表页

### 工具栏按钮

| 按钮 | 定位方式 | 状态 |
|------|--------|------|
| Refresh | 工具栏第一个 icon 按钮 | 始终可用 |
| Export | `buttonByText("Export")` | 始终可用 |
| Setup | `buttonByText("Setup")` | 始终可用 |

> 无创建按钮——计算节点是物理服务器，不可由用户创建。

### 过滤器选项（13 项）

Name、Availability Zone、CPU Architecture、CPU Model、vCPU (Used/Total)、Memory (Used/Total)、Root Disk (Used/Total)、Number of Instances、Number of Devices:USB、Number of Devices:GPU、Enabled、Status、DPDK

### 表格列（11 列）

| 列名 | 可排序 | 说明 |
|------|--------|------|
| Name | ✅ | 节点名称，点击进入详情 |
| Availability Zone | ✅ | 可用域 |
| CPU Architecture/Model | ✅ | 如 Arm / HiSilicon Kunpeng-920 |
| Status | ✅ | Up / Down |
| vCPU (Used/Total) | ✅ | 如 44 / 156，带 info 图标 |
| Memory (Used/Total) | ✅ | 如 56.00GiB / 191.90GiB |
| Root Disk (Used/Total) | ✅ | 如 18.99GiB / 262.69GiB |
| Number of Instances | ✅ | 运行中实例数 |
| Number of Devices | ✅ | 格式: GPU:0 USB:1 NIC:0 |
| Enabled | ✅ | Yes / No |
| Action | ❌ | 操作列 |

### 行操作

| 操作 | 定位方式 | 状态 |
|------|--------|------|
| Instance Batch Live Migration | `agent-browser find text "Instance Batch Live Migration"` | 可用 |
| Instance Batch Cold Migration | `agent-browser find text "Instance Batch Cold Migration"` | 可用 |
| Enable | `agent-browser find text "Enable"` | 节点已启用时禁用 |
| More → Disable | 下拉菜单 | 节点已启用时可用 |

### 表格底部

格式：`Total X items, last updated DD Mon YYYY at HH:mm:ss`

## 节点详情页

### 头部信息

| 元素 | 定位方式 |
|------|--------|
| 返回按钮 | 工具栏左侧箭头 |
| 面包屑 | `button "Compute Node"` → `button "Detail"` |
| More Actions | `buttonByText("More Actions")` |

### Basic Information

| 字段 | 示例值 |
|------|--------|
| Name | node-3501 |
| Availability Zone | default-az |
| CPU Architecture/Model | Arm / HiSilicon Kunpeng-920 |
| Status | Up |
| Enabled | Yes |
| FQDN | node-3501.domain.tld |
| DPDK | Disabled |
| Number of NUMA Nodes | 4 |
| Last Update | 2026-06-16 23:03:55 |

### Virtual Resources

| 指标 | 子分类 |
|------|--------|
| Number of instances | Active: N, Shutoff: N, Other: N |

### Physical Devices

| 设备类型 | 子分类 |
|----------|--------|
| Number of GPU | Mounted / Unmounted |
| Number of vGPU | Mounted / Unmounted |
| Number of USB Devices | Mounted / Unmounted |
| Number of NIC | Virtualized / Not virtualized |
| Number of VF | Attached / Detached |

### Resource Usage Overview

| 资源 | 百分比 | Used | Total |
|------|--------|------|-------|
| vCPU | 百分比 | 数量 | 总量 |
| Memory | 百分比 | 大小 | 总量 |
| Root Disk | 百分比 | 大小 | 总量 |

### 详情页 Tab 页（7 个）

| Tab | 定位方式 | 说明 |
|-----|--------|------|
| Instance | `tab "Instance"` | 默认，该节点上的实例列表 |
| GPU | `tab "GPU"` | GPU 设备列表 |
| vGPU | `tab "vGPU"` | vGPU 设备列表 |
| USB Device | `tab "USB Device"` | USB 设备列表 |
| NIC | `tab "NIC"` | 网卡列表 |
| VF | `tab "VF"` | 虚拟功能列表 |
| NUMA | `tab "NUMA"` | NUMA 拓扑资源使用 |

### Instance Tab 表格列

Name、IP Address、UUID、Virtual Host Name（带 info 图标）、Status

### GPU Tab

工具栏：Refresh、Split to vGPU、Clear vGPU、Enable、Disable、Filter、Export、Setup

表格列：Manufacturer、Product Model、GPU Memory Size、Status、Virtualization Status、All vGPU Count、Available vGPU Count、Attach Resource

### USB Device Tab

表格列：Manufacturer、Product Series、Serial Number、Interface Type、Capacity、Number of Partitions、Mount Status、Attach Resource

### NUMA Tab

信息提示："Shows the resource usage of compute-optimized, network-optimized, and compute-network-optimized instances as mapped to the NUMA topology of their host compute nodes."

NUMA 节点选择按钮：NUMA0、NUMA1、NUMA2、NUMA3

每个 NUMA 节点资源指标：vCPU、Huge pages、Standard Pages（Used / Total + 百分比）

### More Actions 下拉（详情页）

| 操作 | 状态 |
|------|------|
| Instance Batch Live Migration | 可用 |
| Instance Batch Cold Migration | 可用 |
| Enable | 节点已启用时禁用 |
| Disable | 节点已启用时可用 |
| Enable vGPU | 可用 |
| Disable vGPU | 可用 |
