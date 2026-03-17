# Rollback Deployment

A role that allows for quick rollbacks of deployments if they had unintended consequences.

## Variables

- `rollback_deployment_base_dir`: The base directory for IOC deployments. Default is `/epics`.
- `rollback_deployment_iocs_dir`: The directory where all IOCs are stored. Default is `{{ rollback_deployment_base_dir }}/iocs`.
- `rollback_deployment_ioc_dir`: The directory for the specific IOC being rolled back. Default is `{{ rollback_deployment_iocs_dir }}/{{ rollback_deployment_ioc_name }}`.
- `rollback_deployment_ioc_name`: The name of the IOC being rolled back. This variable must be set when using the role.
- `rollback_deployment_num_rollback_steps`: The number of deployments to rollback. Default is `1`.
