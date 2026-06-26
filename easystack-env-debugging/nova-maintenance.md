# Nova Maintenance Pod

Advanced Nova operations (cell management, host maintenance, evacuation, migration debugging)
can affect running workloads. Do not run maintenance commands unless the user explicitly
authorizes the exact operation.

For read-only inspection, first locate the maintenance pod:

```bash
kubectl get pods -n openstack | grep nova-maintenance
kubectl describe pod -n openstack nova-maintenance-<HASH>-<ID>
```

The pod has access to nova management commands and cell database tools. Entering an
interactive shell or running management commands is not a default read-only action.
