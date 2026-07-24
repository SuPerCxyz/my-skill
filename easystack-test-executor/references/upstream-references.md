# Upstream References

## Usage 使用方式

只有 capability、API microversion、support matrix、release behavior 或跨组件影响不确定
时才读取本文件。先匹配目标环境 release, 再使用对应版本文档; 不直接套用 `latest`。

## Core Components 核心组件

| Component | Documentation | API 或关键能力 |
|-----------|---------------|----------------|
| Nova | [Nova](https://docs.openstack.org/nova/latest/) | [Compute API](https://docs.openstack.org/api-ref/compute/), [Support Matrix](https://docs.openstack.org/nova/latest/user/support-matrix) |
| Placement | [Placement](https://docs.openstack.org/placement/latest/) | [Placement API](https://docs.openstack.org/api-ref/placement/) |
| Cinder | [Cinder](https://docs.openstack.org/cinder/latest/) | [Block Storage API](https://docs.openstack.org/api-ref/block-storage/), [Volume Encryption](https://docs.openstack.org/cinder/latest/configuration/block-storage/volume-encryption.html) |
| Glance | [Glance](https://docs.openstack.org/glance/latest/) | [Image API](https://docs.openstack.org/api-ref/image/), [glance_store](https://docs.openstack.org/glance_store/latest/) |
| Neutron | [Neutron](https://docs.openstack.org/neutron/latest/) | [Network API](https://docs.openstack.org/api-ref/network/) |
| Keystone | [Keystone](https://docs.openstack.org/keystone/latest/) | [Identity API](https://docs.openstack.org/api-ref/identity/) |
| Barbican | [Barbican](https://docs.openstack.org/barbican/latest/) | [Key Manager API](https://docs.openstack.org/api-ref/key-manager/), [Castellan](https://docs.openstack.org/castellan/latest/) |
| Ironic | [Ironic](https://docs.openstack.org/ironic/latest/) | [Bare Metal API](https://docs.openstack.org/api-ref/baremetal/), [Boot From Volume](https://docs.openstack.org/ironic/latest/admin/boot-from-volume.html) |
| Connector | [os-brick](https://docs.openstack.org/os-brick/latest/) | Volume connector、attach、detach 和 host residue |
| Workflow | [Taskflow](https://docs.openstack.org/taskflow/latest/) | Retry、revert、persistence 和 flow state |
| Messaging | [oslo.messaging](https://docs.openstack.org/oslo.messaging/latest/) | RPC timeout、retry、notification 和 transport |
| Policy | [oslo.policy](https://docs.openstack.org/oslo.policy/latest/) | Scope、role、policy enforcement 和 upgrade |
| OVN | [OVN](https://www.ovn.org/support/dist-docs/) | Logical flow、binding、NAT 和 controller |
| Ceph | [Ceph](https://docs.ceph.com/en/latest/) | RBD clone、flatten、feature、pool 和 client |

## Clients And Extended Consumers Client 和扩展消费者

- Client behavior: [OpenStackClient](https://docs.openstack.org/python-openstackclient/latest/)
  和 [openstacksdk](https://docs.openstack.org/openstacksdk/latest/)。
- Network consumers: [Octavia](https://docs.openstack.org/octavia/latest/) 和
  [Designate](https://docs.openstack.org/designate/latest/)。
- Storage consumers/backends: [Swift](https://docs.openstack.org/swift/latest/) 和
  [Manila](https://docs.openstack.org/manila/latest/)。
- Orchestration and HA consumers: [Heat](https://docs.openstack.org/heat/latest/) 和
  [Masakari](https://docs.openstack.org/masakari/latest/)。
- Observability consumers: [Ceilometer](https://docs.openstack.org/ceilometer/latest/)、
  [Aodh](https://docs.openstack.org/aodh/latest/) 和 [Gnocchi](https://gnocchi.osci.io/)。
- 其它服务从 [OpenStack API Reference Index](https://docs.openstack.org/api-ref/) 和
  [OpenStack Releases](https://releases.openstack.org/) 定位。

未列出的组件不能直接判定为不受影响。根据调用链、resource consumer、event 和
backend integration 判断是否需要补充上游依据。
