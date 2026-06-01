# Code Debugging via /opt Mount

Many service pods mount the host node's `/opt` directory to `/opt` inside the pod.
This enables a convenient code debugging workflow.

## How It Works

The host `/opt` directory is visible inside the pod at `/opt`.
The host's `/opt` contains service-specific subdirectories
(e.g., `/opt/cinder/`, `/opt/nova-compute/`, `/opt/nova-api-os-compute/`).

## Debugging Workflow

```bash
# Step 1: Copy your debug code to the host node's /opt directory
# e.g., scp to the K8s node, or use the interactive SSH shell to paste it
scp <your-code.py> root@<TARGET_NODE_IP>:/opt/<service>/

# Step 2: Exec into the pod
kubectl exec -it -n openstack <pod-name> -- /bin/bash

# Step 3: Inside the pod, copy from /opt to overwrite the pod's internal code
# Find the target location (typically Python site-packages inside the container)
cp /opt/<service>/<your-code.py> /path/to/original/<your-code.py>

# Step 4: Restart the service or reload the module
/tmp/<service>.sh stop
/tmp/<service>.sh start
```

## Common /opt Locations

| Service | Host /opt Path | Pod Mount |
|---------|---------------|-----------|
| cinder-volume | `/opt/cinder/` | `/opt/cinder/` |
| nova-compute | `/opt/nova-compute/` | `/opt/nova-compute/` |
| nova-api-os-compute | `/opt/nova-api-os-compute/` | `/opt/nova-api-os-compute/` |
