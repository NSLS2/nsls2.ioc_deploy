# nsls2.ioc_deploy

Ansible collection meant for centralizing deployment logic for EPICS IOC instances.

The `nsls2.ioc_deploy` collection expects to be used in tandem with two other repositories; one with the playbooks that call these roles with some input parameters, and another repository for storing IOC instance configurations.

The collection includes several core central roles that are shared by all deployments, and then one role per type of IOC/hardware, found under `roles/`. Each IOC type also has a `vars` file for overriding default behaviors in `roles/deploy_ioc/vars/`.
Any required EPICS modules can be automatically built by the `install_module` role. The configured modules can be seen at `roles/install_module/vars/`.

## Local Testing

This requires a python environment with ansible installed, and docker or podman.

To get the latest EPICS container for local testing:

```bash
docker pull ghcr.io/nsls2/epics-alma8:latest
docker run -dit --name epics-dev ghcr.io/nsls2/epics-alma8:latest
```

Test IOC role locally against an EPICS container:

```bash
./scripts/test-role.sh <role-name>
```
