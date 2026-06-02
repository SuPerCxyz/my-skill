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

# Step 2: Edit the startup script so it copies code from /opt into the runtime package path first
# Example:
cp -rf /opt/<service>/* /path/to/site-packages/<service>/

# Step 3: Let the pod continue normal startup
# Keep the original launch path so logs stay visible through kubectl logs
exec /usr/bin/python3 -m <service>.main
```

## Common /opt Locations

| Service | Host /opt Path | Pod Mount |
|---------|---------------|-----------|
| cinder-volume | `/opt/cinder/` | `/opt/cinder/` |
| nova-compute | `/opt/nova-compute/` | `/opt/nova-compute/` |
| nova-api-os-compute | `/opt/nova-api-os-compute/` | `/opt/nova-api-os-compute/` |
