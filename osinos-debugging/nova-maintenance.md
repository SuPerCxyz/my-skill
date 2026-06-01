# Nova Maintenance Pod

Advanced Nova operations (cell management, host maintenance, evacuation, migration debugging)
should be done in the `nova-maintenance` pod:

```bash
kubectl exec -it -n openstack nova-maintenance-<HASH>-<ID> -- /bin/bash
```

The pod has access to nova management commands and cell database tools.
