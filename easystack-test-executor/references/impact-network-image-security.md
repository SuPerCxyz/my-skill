# Network Image Security Impact Matrix

## Network 网络

Neutron 改动至少展开 Network、Subnet、Port、Router、Floating IP、Security Group、
DHCP、metadata 和 backend agent/controller。API 状态不能替代 dataplane 连通性。

| 改动点 | 关联测试 | 失败后检查 |
|--------|----------|------------|
| Port binding | Server create、attach interface、migration、SR-IOV | binding profile、host、VIF、allocation |
| Security Group | ingress/egress、IPv4/IPv6、remote IP/group、stateful | rule 下发、已有 Port、残留 flow |
| Floating IP | create、associate、reassociate、disassociate、delete | Port relation、NAT、address 回收 |
| Router | interface、external gateway、SNAT、HA/DVR | namespace/controller、route、Port 残留 |
| Subnet | allocation pool、DNS、gateway、DHCP、IPv6 RA | IPAM allocation、DHCP lease、Port |

Network 功能结果分层记录: Neutron resource state、Port binding、控制面规则、VM 内地址、
同网段/跨网段/公网连通性。无法进入 guest 时不能把 API 成功写成 dataplane 成功。

## Image 镜像

Glance 改动按 upload、download、import、copy、visibility、member、format、property 和
consumer 展开:

- 测试创建 Image 默认 `public`, 除非用例明确验证其它 visibility。
- 业务命令统一使用 `openstack image ...`, 不固化 legacy `glance` client。
- raw、qcow2、container format、virtual size 和 checksum 会影响 Cinder from-image、
  Nova boot、conversion 和 cache。
- Image active 之后分别验证 Nova Boot Volume、Cinder Volume、download 或数据校验。
- import/copy 失败检查 staging、store、task 和临时对象残留。
- 删除或不可见 Image 时验证已有 Volume/Server 不被错误影响, 新请求按产品语义拒绝。

## Security 安全

Security 不是单一服务。按 Keystone policy、Project isolation、Barbican Secret、
Neutron Security Group、Glance visibility 和日志脱敏分别展开:

- Positive 和 negative 用户/Project, 包括 owner、member、admin 和无权限主体。
- Token、Secret、key、password 只验证 ID、权限和错误语义, 不输出 payload。
- Policy 改动覆盖 list/show/create/update/delete 的资源范围和信息泄露。
- Security Group 使用 `openstack security group ...`, 验证规则对象和 dataplane。
- Barbican 改动关联 Cinder encryption、Nova encrypted attach、Secret delete/expiry 和
  Project ownership。
- Audit/worker 日志必须脱敏, 但保留 Request ID、resource ID、service、Pod 和时间窗。

## Cross-Domain Checks 跨域检查

- Image visibility 影响 Cinder/Nova 可见性和缓存复用。
- Port Security 与 Security Group、allowed address pair、trunk、SR-IOV 能力有关。
- Floating IP 默认随 Server 用例创建和绑定, 但清理时先解关联再删除。
- 任何 Network/Image/Security 变更都要验证已有资源回归和新资源路径, 不能只测新建。
