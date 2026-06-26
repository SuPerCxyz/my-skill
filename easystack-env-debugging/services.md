# Services Discovery

Use this file when mapping service names to pod prefixes, ports, namespaces, or repo locations. For concrete log commands, use [logs.md](logs.md); for authentication, use [auth.md](auth.md).

## Core OpenStack Services

| Service | Pod Prefix | Admin Port | Description |
|---------|-----------|-----------|-------------|
| Keystone | `keystone-api-*` | internal via cluster | Identity service |
| Glance | `glance-api-0,1,2` | 9292 | Image service (StatefulSet) |
| Nova | `nova-api-osapi-*`, `nova-compute-*`, `nova-conductor-*`, `nova-scheduler-*`, `nova-maintenance-*` | 8774 | Compute service |
| Cinder | `cinder-api-*`, `cinder-scheduler-*`, `cinder-volume-*` | 8776 | Block storage |
| Cinder Golem | `cinder-golem-*` | 8192 | Cinder dashboard 后端 API(端口 8192) |
| Aodh | `aodh-api-*`, `aodh-evaluator-*`, `aodh-notifier-*` | 8042 | Alarming |
| Ceilometer | `ceilometer-api-*`, `ceilometer-collector-*` | 8777 | Telemetry |
| Gnocchi | `gnocchi-api-*`, `gnocchi-metricd-*` | - | Metrics storage |
| Horizon | `horizon-*` | 80 | OpenStack dashboard |

## Ironic Namespace

Ironic services run in the independent `ironic` namespace. Do not assume they are
in `openstack`. The exception is `nova-compute-ironic`, which belongs to the
Nova side and may appear under the OpenStack deployment layout.

```bash
kubectl get pods -n ironic
kubectl get pods -n ironic --show-labels
kubectl get pods -n openstack -l service=nova-compute-ironic
```

## Networking (OVN Mode)

No standalone `neutron-server` pods. Networking handled by:

| Pod Pattern | Role |
|-------------|------|
| `ovn-controller-*` | OVN controller agent on each compute node (DaemonSet) |
| `ovn-northd-0,1,2` | OVN Northd daemon (StatefulSet) |
| `ovn-ovsdb-nb-0,1,2` | OVN northbound database |
| `ovn-ovsdb-sb-0,1,2` | OVN southbound database |
| `ovn-ovsdb-nb-relay-*` / `ovn-ovsdb-sb-relay-*` | Database relays |
| `proton-ovn-gateway-monitor-agent-*` | Gateway monitoring |
| `proton-ovn-metadata-agent-*` | Metadata agent |
| `proton-ovn-l2gw-agent-*` | L2 gateway agent |

Neutron config inspection: `kubectl get cm -n openstack neutron-etc -o yaml`.

## Helm Releases

Most OpenStack control-plane releases are deployed via Helm in `openstack`
namespace. Check service-specific namespaces such as `ironic` separately:

| Helm Release | Chart Version | Covers |
|-------------|---------------|--------|
| `keystone` | `keystone-7.0.1-alpha.83` | Identity |
| `glance` | `glance-7.0.1-alpha.20` | Image service |
| `nova` | `nova-7.0.1-alpha.109` | Compute |
| `cinder` | `cinder-7.0.1-alpha.21` | Block storage |
| `ceilometer` | `ceilometer-7.0.1-alpha.8` | Telemetry |
| `horizon` | `horizon-7.0.1-alpha.83` | Dashboard |
| `mariadb` | `mariadb-7.0.1-alpha.83` | Database |
| `rabbitmq` | `rabbitmq-7.0.1-alpha.83` | Message queue |
| `memcached` | `memcached-7.0.1-alpha.83` | Cache |
| `redis` | `redis-7.0.1-alpha.83` | Redis |
| `mongodb` | `mongodb-7.0.1-alpha.83` | MongoDB |
| `chartmuseum` | `chartmuseum-7.0.1-alpha.83` | Helm chart repo |

```bash
helm list -n openstack
helm history -n openstack <release-name>
```

`helm get values -n openstack <release-name>` is read-only, but some environments
return `Unauthorized operation`. Treat it as optional and do not block the
inspection flow if it fails.

`helm rollback` changes the environment. Do not run it unless the user explicitly
authorizes that exact rollback.

## Project Code Layout

Each component typically has 3-4 repositories:

| Repository | Purpose | Pod Name Pattern |
|------------|---------|-----------------|
| `<service>` (e.g., `nova`) | Core service code | `<service>-*` |
| `ark-<service>` (e.g., `ark-nova`) | Management config and startup scripts | Same pods, scripts in `/tmp/` |
| `<service>-dashboard` | Frontend UI | `<service>-dashboard-*` |
| `<service>-dashboard-api` | Frontend backend API | `<service>-dashboard-api-*` |

**Cinder exception:** dashboard API is `golem`, pod is `cinder-golem-*`:

| Component | Backend | Config/Scripts | Frontend UI | Frontend API |
|-----------|---------|---------------|-------------|-------------|
| Nova | `nova` | `ark-nova` | `nova-dashboard` | `nova-dashboard-api` |
| Cinder | `cinder` | `ark-cinder` | `cinder-dashboard` | `golem` |
| Glance | `glance` | `ark-glance` | `glance-dashboard` | `glance-dashboard-api` |

These are repository names. Source code is **not** on nodes by default - only packaged service code runs in pods.

## Custom/Extended Services

| Service | Pod Prefix | Description |
|---------|-----------|-------------|
| easystack-cache | `easystack-cache-api-*` | Cache service |
| EMLA | `emla-apiserver-*`, `emla-controller-*` | Resource management |
| ESDM | `esdm-api-*` | Service data management |
| Proton | `proton-server-*`, `proton-dashboard-*` | Custom networking |
| Roller | `roller-dashboard-*` | Custom dashboard |
| OTA | `ota-openapi-*`, `ota-dashboard-*` | OTA service |
| Coaster | `coaster-all-*` | Orchestration |

## Infrastructure Pods

| Pod | Description |
|-----|-------------|
| `mariadb-0,1,2` | Database (StatefulSet) |
| `rabbitmq-0,1,2` | Message queue (StatefulSet) |
| `memcached-*` | Cache |
| `redis-*` | Redis |
| `mongodb-*` | MongoDB |
| `chartmuseum-*` | Helm chart repository |
| `services/busybox` | Debugging pod with OpenStack CLI (service selector, no need to know pod name) |
