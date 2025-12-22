# nsls2.ioc_deploy

Ansible collection meant for centralizing deployment logic for EPICS IOC instances.

The `nsls2.ioc_deploy` collection expects to be used in tandem with two other repositories; one with the playbooks that call these roles with some input parameters, and another repository for storing IOC instance configurations.

The collection includes several core central roles that are shared by all deployments, and then one role per type of IOC/hardware, found under `roles/`. Each IOC type also has a `vars` file for overriding default behaviors in `roles/deploy_ioc/vars/`.
Any required EPICS modules can be automatically built by the `install_module` role. The configured modules can be seen at `roles/install_module/vars/`.

## Contributing

### Adding a new installable module

If you require an EPICS module as a dependency, but don't plan on deploying it as an IOC, then you can make only the module.

```bash
pixi run make-module
```

Follow the prompts to get started. See [install_module](roles/install_module/README.md) for a full reference on supported options.

You can then add this module to the `module_deps` of any device role.

### Adding a new device role

If you have a new EPICS module that you also plan to deploy as an IOC, then you can make a device role. This will also
prompt you to make the installable module.

```bash
pixi run make-role
```

Follow the prompts to get started. See [deploy_ioc](roles/deploy_ioc/README.md) and [install_module](roles/install_module/README.md) for full references on supported options. Furthermore, if a similar device exists (it probably does), then browse the [device_roles](roles/device_roles/) before starting.

There are a few required items to help make this repository more maintainable. They are:
- a `schema.yml` defining how to configure the role for deployment
- an `example.yml` to demonstrate a working example

You can deploy your `example.yml` easily. Please see the section on [Local Testing](#local-testing).

### Updating an existing role or module

Simply make changes to the device role and submit a pull request to this repository. Breaking changes to existing schemas will need to be justified.

#### Special Case: New version of the module source code

If you require a new version of the IOC, you will need to [add a new installable module](#adding-a-new-installable-module) with that specific Git commit hash. Then, you can override the `deploy_ioc_required_module` of the existing device role to point to this new installable module.

If the newest version is not a major release (i.e. does not contain breaking changes), then you can likely update the existing installable module to use the new Git commit hash. Be sure to extensively test with real hardware before and after doing this.

You can update the module by running:
```bash
pixi run update-module
```

> [!NOTE]
> Maintainers of this repository will periodically update important installable modules to keep up with version changes. Please submit an issue if you notice we are behind.

## Local testing

This requires pixi and docker or podman.

To get the latest EPICS container for local testing:

```bash
docker login ghcr.io
docker pull ghcr.io/nsls2/epics-alma8:latest
docker run -dit --name epics-dev ghcr.io/nsls2/epics-alma8:latest
```

Test IOC role locally against an EPICS container:

```bash
pixi run test-role <role-name>
```

## Helper scripts

Run using `pixi run <command>`.

| Command | Purpose |
|---------|---------|
| `make-role` | Make a new deployment role |
| `make-module` | Make a new installable module |
| `update-module` | Update an existing installable module |
| `delete-role` | Remove an existing deployment role |
| `delete-module` | Remove an existing installable module |
| `report` | View the status of this Ansible collection |
| `lint` | Run the linter to check for errors |
| `lint-changes` | Lint only the changed files |
| `tests` | Run tests |
| `test-role` | Test deploying a role using [a local container](#local-testing) |
