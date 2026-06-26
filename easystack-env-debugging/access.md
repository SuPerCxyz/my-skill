# Environment Access

## 访问环境后台

默认只做查看操作。连接成功后，优先执行 `whoami`、`id -u`、`hostname`、`pwd`、
`kubectl get`、`kubectl describe`、`kubectl logs --tail=<N>` 等无影响命令。
不要在未获得明确授权时执行 `edit/delete/apply/patch/rollout restart/helm rollback` 等变更命令。

### 示例入口

| 示例 | 模式 | 典型落点 |
|------|------|----------|
| `192.168.3.3` | 直连模式 | `root@node-1.domain.tld` |
| `172.18.0.118` | 跳板机模式，内层默认到 `10.20.0.3` | 外层 `root@x8-f-install-7-0-1-alpha-103-jump-server-k2deji6cqvck.novalocal`，内层 `root@node-6.domain.tld` |
| `BJ-35` | JumpServer 模式 | `root@node-3501.domain.tld` |

## 跳板机模式(IP 以 172.18. 开头)

```bash
# 一步执行只读验证命令
sshpass -p "easystack" ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP> "whoami; id -u; hostname; pwd"'

# 交互式会话
sshpass -p "easystack" ssh -tt -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<JUMP_IP> 'ssh -F /dev/null -i /root/.ssh/id_rsa.roller -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<CONTROL_NODE_IP>'
```

- `<JUMP_IP>` 由用户指定(如 `172.18.0.118`、`172.18.0.133`、`172.18.0.242`)
- `<CONTROL_NODE_IP>` 通常为 **10.20.0.3**，失败时询问用户
- 跳板机本身没有 kubectl，必须内层 SSH 到控制节点
- 示例环境 `172.18.0.118 -> 10.20.0.3` 可执行 `kubectl get/describe/logs`、
  `helm list/history`、`kubectl get cm -o yaml`、busybox 中的
  `openstack server list` 和 `openstack volume list`

## 直连模式(非 172.18. 开头)

```bash
# 直接 SSH 到 K8s 控制节点
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 root@<TARGET_IP>

# 只读验证
ssh -F /dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 root@<TARGET_IP> 'whoami; id -u; hostname; pwd'
```

- 如果密码错误，先试 `easystack`，再问用户
- 示例: `192.168.3.3`

## SSH 直连/跳板补充说明

- **复杂命令避免嵌套 SSH 引号传递** — 无论是跳板机双层 SSH 还是直连后跳 node，引号和变量展开都容易丢失。优先进入交互式会话再执行
- 直连和 `172.18.*` 跳板模式不依赖本机 SSH 配置，按命令中的密码或密钥连接
- **不要从本机直连 K8s 节点内网 IP**(如 10.10.1.x)，必须通过控制节点中转
- `easystack` 密码可能因环境不同，未知时询问用户
- 默认只允许查看操作；变更操作必须获得用户明确授权

## JumpServer 堡垒机模式

部分环境通过 JumpServer 堡垒机管理，而非直接 SSH 到 K8s 控制节点。

### 连接流程

```
选择 JumpServer 入口          → 根据环境类型选择测试或生产 JumpServer
ssh -tt -F ~/.ssh/config <SSH_ALIAS> → 优先读取用户 SSH 配置进入 JumpServer 控制台
输入目标资产名(如 BJ-32)      → JumpServer 代理 SSH 到目标主机
sudo su -                     → 切换到 root
```

### JumpServer 入口选择

| 环境类型 | JumpServer | 说明 |
|----------|------------|------|
| 类似 `BJ-xx` 的测试环境 | `js.easystack.io:2222` | 用于访问测试环境资产 |
| x86 / arm 生产环境 | `jumpserver.easystack.cn:2222` | 用于访问生产环境资产 |

### JumpServer 前置条件与配置缺失处理

- 优先使用用户 SSH 配置中的 alias，例如 `ssh -tt -F ~/.ssh/config <SSH_ALIAS>`。
- skill 默认不展开 HostName、Port、User 或 IdentityFile。
- 如果 `~/.ssh/config` 中没有对应 alias，不要猜测账号或密钥。先根据环境类型
  选择 JumpServer host，再向用户补齐:
  - 目标资产名或环境名
  - 环境类型: 测试环境(`BJ-xx` 类)或 x86 / arm 生产环境
  - 如果已有用户 SSH 配置: 对应的 `<SSH_ALIAS>`
  - JumpServer 用户名
  - 认证方式: 密钥路径、密码或是否有 MFA/交互确认
- 用户补齐后，可用一次性 SSH 命令进入 JumpServer，不必写入 `~/.ssh/config`:
  ```bash
  ssh -tt -p 2222 -i <IDENTITY_FILE> <USER>@<JUMPSERVER_HOST>
  ```
  如果使用密码认证，去掉 `-i <IDENTITY_FILE>`，按交互提示输入密码。

### 交互式使用(expect 脚本)

JumpServer 是交互式 TUI 菜单，无法通过管道直接输入。使用 expect 脚本完成自动登录。
默认使用用户 SSH 配置中的 alias，通过 `-F ~/.ssh/config` 避免系统级
`/etc/ssh/ssh_config.d` 配置干扰；不要加 `-F /dev/null` 绕过用户配置。

```bash
#!/usr/bin/expect -f
set timeout 30
set jumpserver_alias "SSH_ALIAS"
set asset_name "ASSET_NAME"

# 连接 JumpServer,显式读取用户 SSH 配置
spawn ssh -tt -F ~/.ssh/config $jumpserver_alias

# 如果 ~/.ssh/config 没有对应 alias,先向用户补齐 USER/JUMPSERVER_HOST/IDENTITY_FILE,
# 再把上一行替换为一次性连接命令:
# spawn ssh -tt -p 2222 -i <IDENTITY_FILE> <USER>@<JUMPSERVER_HOST>
# 密码认证时去掉 -i <IDENTITY_FILE>

# 等待菜单提示符
expect {
    "Opt>" {
        send_user "已进入 JumpServer 菜单\n"
    }
    "Bad owner or permissions" {
        send_user "用户 SSH 配置权限异常,请检查 ~/.ssh/config 及其 include 文件\n"
        exit 1
    }
    "Permission denied" {
        send_user "JumpServer SSH 认证失败\n"
        exit 1
    }
    timeout {
        send_user "等待 JumpServer 菜单超时\n"
        exit 1
    }
}

# 发送目标资产名
send "$asset_name\r"

# 等待 JumpServer 开始连接资产,避免把菜单里的 Opt> 误判为资产 shell
expect {
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    -re {开始连接到|Last login|Authorized users only} {
        exp_continue
    }
    -re {\[[^]]+@[^]]+[[:space:]]+[^]]+\][#$][[:space:]]*$} {
        send_user "已连接到目标资产\n"
    }
    timeout {
        send_user "连接目标资产超时\n"
        exit 1
    }
}

# 切换到 root
send "sudo su -\r"
expect {
    -re {\[root@[^]]+[[:space:]]+[^]]+\]#[[:space:]]*$} {
        send_user "已切换到 root\n"
    }
    "not in the sudoers" {
        send_user "没有 sudo 权限\n"
        exit 1
    }
    "password" {
        send_user "sudo su - 需要密码,请人工处理或提供密码\n"
        exit 1
    }
    timeout {
        send_user "切换 root 超时,可能需要密码或 prompt 格式不同\n"
        exit 1
    }
}

# 进入交互模式
send "cd ~\r"
interact
```

### 常见资产名

| 名称 | 说明 |
|------|------|
| `BJ-32` (node-3202, 172.32.0.2) | 北京 32 环境 |
| *(其他资产由用户指定)* | |

### 常见资产内特征

| 属性 | 说明 |
|------|------|
| 登录用户 | 常见为 `dev` (JumpServer 系统用户)，以实际登录结果为准 |
| sudo 权限 | 常见为 NOPASSWD，可免密 `sudo su -`，以实际资产权限为准 |
| root 验证 | `whoami` 返回 `root`，`id -u` 返回 `0` |
| 额外组 | 可能包含 `pamauth` (1000)，以实际 `id` 输出为准 |
| JumpServer 复用 | 部分资产支持复用 SSH 连接 |

### 注意事项

- JumpServer TUI 菜单支持: 输入资产名(唯一时自动登录)、`/ + IP/名称` 搜索、`p` 列出有权限的主机
- 如果 `sudo su -` 需要密码，说明不是 NOPASSWD 配置，需询问用户密码
- 这种方式与 jump host 模式、直连模式并列，是第三种环境访问路径

## 进入后台后

以下步骤适用于直连、`172.18.*` 跳板、JumpServer 三种模式。默认只做查看操作。

### 连接验证

进入目标主机并切到 root 后，先做最小只读验证:

```bash
whoami       # 应返回 root
id           # uid=0(root)
hostname
pwd
```

如果目标节点具备 kubectl 和 kubeconfig，再执行 Kubernetes 只读验证:

```bash
kubectl get namespaces | grep openstack
kubectl get pods -n openstack | head
```

### 节点间跳转

始终使用主机名而非 IP 地址访问其他节点。节点有多个 IP 分布在管理网、
存储网、VXLAN 等多个网平面；`/etc/hosts` 由部署工具维护，解析到当前
可用的正确网络路径。直接使用 IP 可能会指定到有问题的网络，导致误判或
SSH 不通。

```bash
# 正确: 使用主机名访问其他节点(节点间通常已配免密)
ssh node-3 'hostname; whoami; pwd'

# 不要直接用 IP
ssh 32.168.40.2 'command'  # 可能选了存储网而非管理网
```
