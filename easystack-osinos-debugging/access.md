# Environment Access

## SSH Chain

```bash
sshpass -p "easystack" ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@<JUMP_IP> 'ssh -i .ssh/id_rsa.roller <TARGET_NODE_IP>'
```

- `<JUMP_IP>` varies per environment (e.g., `172.18.0.133`)
- `<TARGET_NODE_IP>` is the K8s node IP (e.g., `10.20.0.3`)
- The `easystack` password may change per environment — ask the user if unknown

## Interactive SSH Shell

For extended debugging sessions, open an interactive shell on the target node:

```bash
sshpass -p "easystack" ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@<JUMP_IP> 'ssh -i .ssh/id_rsa.roller <TARGET_NODE_IP>'
```

From there you can run any `kubectl` command interactively without re-wrapping each call.

## SSH + kubectl in One Command

```bash
sshpass -p "easystack" ssh -tt -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@<JUMP_IP> 'ssh -i .ssh/id_rsa.roller <TARGET_NODE_IP>' "<kubectl-command>"
```

**Note:** `for` loops and complex shell scripts cannot be run through the nested SSH quoting.
For those, first enter the interactive SSH shell, then run the script there.

## Local OpenStack Client via Endpoint Mapping

The jump host runs APISIX which routes requests by Host header.
Add all endpoint hostnames to `/etc/hosts` pointing to the jump host IP,
then install `python-openstackclient` locally:

```bash
# Step 1: Add endpoints to /etc/hosts (map to jump host IP)
<JUMP_IP> aodh-api.openstack.svc.cluster.local aodh.openstack.svc.cluster.local ceilometer-api.openstack.svc.cluster.local ceilometer.openstack.svc.cluster.local ceph-rgw.ceph.svc.cluster.local ceph-rgw-ingress.ceph.svc.cluster.local cinder-api.openstack.svc.cluster.local cinder.openstack.svc.cluster.local coaster-all.openstack.svc.cluster.local coaster.openstack.svc.cluster.local emla-apiserver.openstack.svc.cluster.local emla.openstack.svc.cluster.local glance-api.openstack.svc.cluster.local glance.openstack.svc.cluster.local gnocchi-api.openstack.svc.cluster.local gnocchi.openstack.svc.cluster.local keystone-api.openstack.svc.cluster.local keystone.openstack.svc.cluster.local neutron.openstack.svc.cluster.local neutron-server.openstack.svc.cluster.local nova-api.openstack.svc.cluster.local nova.openstack.svc.cluster.local peak-api.ems.svc.cluster.local peak.ems.svc.cluster.local placement-api.openstack.svc.cluster.local placement.openstack.svc.cluster.local

# Step 2: Install openstack client
pip install python-openstackclient

# Step 3: Set environment variables (use publicURL — APISIX routes via Host header)
export OS_IDENTITY_API_VERSION=3
export OS_USERNAME=admin
export OS_PASSWORD='<PASSWORD>'        # default: Admin@ES20!8
export OS_AUTH_URL='http://keystone.openstack.svc.cluster.local:80/v3'
export OS_REGION_NAME=RegionOne
export OS_INTERFACE=publicURL
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
```

Now run `openstack` commands directly: `project list`, `server list`, `volume list`, etc.

**Why publicURL:** APISIX on the jump host only exposes port 80.
Services with `internalURL`/`adminURL` on non-standard ports are not accessible.

## Local vs Busybox CLI — When to Use Each

| Scenario | Where to Run | Why |
|----------|-------------|-----|
| `project list`, `server list`, `volume list` | Local | Fast, no SSH needed |
| `server show`, `volume show`, `endpoint list` | Local | Metadata-only |
| `image create` / large file uploads | Busybox pod | Cluster-internal network faster |
| Operations requiring `adminURL` endpoints | Busybox pod | `adminURL` not routed through APISIX |
| Generate/download files then upload | Busybox pod | Download directly to cluster storage |

Example: upload image from busybox pod:
```bash
kubectl exec -it -n openstack services/busybox -- bash
# Inside busybox:
wget http://example.com/image.qcow2 -O /tmp/image.qcow2
openstack image create --file /tmp/image.qcow2 --disk-format qcow2 --container-format bare my-image
```
