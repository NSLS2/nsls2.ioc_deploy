# CI Workflows

The repository uses GitHub Actions for continuous integration. Three workflows validate changes at different levels.

## Workflow Overview

| Workflow | Trigger | What It Tests |
|----------|---------|---------------|
| `validate_module_configs.yml` | All PRs and pushes to main | Schema validation of all config files |
| `test-device-roles.yml` | PRs modifying device roles or vars | Full deployment test of modified roles |
| `test-deploy-ioc-role.yml` | PRs modifying core roles | Core deployment logic with sample IOCs |

## Validate Configurations (`validate_module_configs.yml`)

**Runs on:** Every push to `main` and every PR.

This workflow runs the pytest suite in three stages:

1. **Validate Module Vars Files** — Ensures all `roles/install_module/vars/*.yml` files conform to `schemas/install_module.yml`
2. **Validate Device Specific Roles** — Checks that every device role has a corresponding vars file, and vars files are valid
3. **Validate Example Configs** — Verifies that example configurations pass their role's schema validation

```yaml
# Simplified flow
pixi run tests tests/test_install_module_vars.py
pixi run tests tests/test_deploy_ioc_vars.py tests/test_device_roles.py
pixi run tests tests/test_validate_ex_configs_against_schemas.py
```

## Test Device Roles (`test-device-roles.yml`)

**Runs on:** PRs that modify files under `roles/device_roles/` or `roles/deploy_ioc/vars/`.

This workflow:

1. **Detects which roles were modified** in the PR (or tests all roles on manual dispatch)
2. **Runs a matrix build** testing each modified role on both EL 8 and EL 9
3. **Deploys each role** into a container using `pixi run deployment -t <role> --container -m <version>`

### Change Detection Logic

The workflow only tests roles that were actually modified:

- Changes to `roles/device_roles/<name>/` → test that role
- Changes to `roles/deploy_ioc/vars/<name>.yml` → test that role
- Manual workflow dispatch → test ALL roles

### Matrix Strategy

```yaml
strategy:
  matrix:
    role: ${{ fromJson(needs.detect-changes.outputs.roles) }}
    rhel_version: [8, 9]
  fail-fast: false
```

Each role × EL version combination runs independently, so one failure doesn't block others.

## Test Deploy IOC Role (`test-deploy-ioc-role.yml`)

**Runs on:** PRs that modify core role logic (but NOT vars files, which are covered by the device roles workflow).

Tests specific IOC archetypes to exercise different code paths:

- **Python IOC** (`pandabox`) — Tests non-standard startup, pixi-based deployment
- **Compiled IOC** (`powerpmac`, `rbd9103`) — Tests full module compilation + deployment

Paths that trigger this workflow:

```yaml
paths:
  - 'roles/deploy_ioc/**'
  - 'roles/install_module/**'
  - '!roles/deploy_ioc/vars/**'       # Excluded (tested by device roles workflow)
  - '!roles/install_module/vars/**'   # Excluded (tested by device roles workflow)
```

## Adding CI Coverage for a New Role

When you add a new device role, CI coverage is **automatic**:

1. The `validate_module_configs` workflow validates your schema, example, and module config
2. The `test-device-roles` workflow will test your role whenever its files are modified in a PR

### Requirements for CI to Pass

Your role must have:

- A valid `schema.yml` that passes yamale validation
- An `example.yml` (or `examples/<name>/config.yml`) that conforms to the schema
- A vars file at `roles/deploy_ioc/vars/<role-name>.yml`
- A module config referenced by `deploy_ioc_required_module` (if applicable)
- All `module_deps` must reference existing module vars files

### Handling Roles That Need Proprietary SDKs

Some roles (e.g., certain camera drivers) require proprietary SDKs that aren't available in CI. Use `skip_compilation` in `verify.yml`:

```yaml
---
skip_compilation: true

verification:
  files_must_exist:
    - iocBoot/st.cmd
    - iocBoot/base.cmd
  # ... structural checks only
```

The deployment script will pass `--skip-compilation` when this flag is set, allowing the role to be structurally validated without actually compiling the module.

## Running CI Locally

You can replicate the CI environment locally:

```bash
# Run the same validation tests as CI
pixi run tests

# Deploy a specific role like CI does
pixi run deployment -t adsimdetector --container -m 8
pixi run deployment -t adsimdetector --container -m 9

# Test all roles (equivalent to manual workflow dispatch)
pixi run deploy-all
```
