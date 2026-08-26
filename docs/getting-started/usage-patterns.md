# Usage Patterns

## Intended Workflow

The `nsls2.ioc_deploy` collection is designed to be used in a **three-repository architecture**:

```
┌─────────────────────────┐     ┌─────────────────────────────┐
│  nsls2.ioc_deploy       │     │  Playbook Repository        │
│  (this collection)      │     │  (calls roles with params)  │
│                         │     │                             │
│  • Core deployment logic│◄────│  • Defines what to deploy   │
│  • Device roles         │     │  • Sets host_config         │
│  • Module configs       │     │  • Specifies targets        │
└─────────────────────────┘     └──────────────┬──────────────┘
                                               │
                                               ▼
                                ┌─────────────────────────────┐
                                │  IOC Config Repository      │
                                │  (per-beamline configs)     │
                                │                             │
                                │  • IOC instance definitions │
                                │  • Environment variables    │
                                │  • Substitution files       │
                                └─────────────────────────────┘
```

1. **This collection** (`nsls2.ioc_deploy`) — Contains the reusable Ansible roles and device-specific logic
2. **A playbook repository** — Calls these roles with appropriate parameters for a given deployment
3. **An IOC configuration repository** — Stores per-beamline, per-IOC instance configurations

## IOC Configuration Format

Each IOC instance is defined as a YAML dictionary entry. The key is the IOC name, and the value contains its configuration:

```yaml
my-ioc-01:
  type: adaravis                    # Must match a device role name
  environment:                       # Required environment variables
    ENGINEER: "J. Smith"
    PREFIX: "XF:28ID1-ES{Cam:1}"
    CAMERA_NAME: "Allied Vision-Manta G-040B-50-0503548886"
    ENABLE_CACHING: 1
```

The `type` field determines which device role is applied. Each device role defines a schema that validates the configuration structure.

## Deployment Flow

When a deployment is triggered, the following sequence occurs:

1. **Host configuration** is loaded (network interface, user/group, base paths)
2. **System packages** are installed (e.g., `procServ`)
3. **Network setup** file is deployed for EPICS Channel Access
4. For each IOC instance:
    1. The IOC `type` field selects the appropriate **device role vars** from `roles/deploy_ioc/vars/<type>.yml`
    2. The `install_module` role builds any required EPICS modules (with full dependency resolution)
    3. The **core `deploy_ioc` tasks** create directory structure, startup scripts, and environment files
    4. The **device-specific tasks** from `roles/device_roles/<type>/tasks/main.yml` run to customize the deployment
    5. Optionally, the IOC service is installed, enabled, and/or started

## Variable Precedence

Variables are resolved in the following order (highest priority first):

1. **IOC instance configuration** (from the config repository)
2. **Device role vars** (`roles/deploy_ioc/vars/<type>.yml`)
3. **Device role defaults** (`roles/device_roles/<type>/defaults/main.yml`)
4. **deploy_ioc defaults** (`roles/deploy_ioc/defaults/main.yml`)

## Standard vs. Custom Startup Scripts

Most IOCs use the **standard startup script** format (`deploy_ioc_standard_st_cmd: true`), which produces:

```
<ioc-dir>/
├── st.cmd                  # Top-level wrapper script
├── iocBoot/
│   ├── st.cmd              # Main startup script (loads all .cmd files, runs iocInit)
│   ├── epicsEnv.cmd        # Environment variable definitions
│   ├── base.cmd            # Device-specific initialization (from device role template)
│   ├── common.cmd          # Common module loading (iocStats, autosave, etc.)
│   └── postInit.cmd        # Post-initialization commands (dbpf, etc.)
├── db/
│   └── *.substitutions     # Database substitution files
└── as/
    ├── req/                # Autosave request files
    └── save/               # Autosave save files
```

For IOCs that need completely custom startup (e.g., Python-based caproto IOCs), set `deploy_ioc_standard_st_cmd: false`.

## Python-Based IOCs

Some IOC types (e.g., `pandabox`) are Python-based and use `pixi` for environment management instead of compiled EPICS binaries. These roles:

- Set `deploy_ioc_standard_st_cmd: false`
- Manage their own startup scripts
- Use `deploy_ioc_pixi_executable_path` for the pixi binary location

## Post-Deployment Actions

The `deploy_ioc_post_deploy_step` variable controls what happens after files are deployed:

| Value | Behavior |
|-------|----------|
| `"None"` | Deploy files only, don't touch services |
| `"Install"` | Install the systemd service file |
| `"Install and Enable"` | Install and enable (auto-start on boot) |
| `"Install and Start"` | Install and start immediately |
| `"Install and Enable and Start"` | Install, enable, and start |
| `"Restart"` | Restart an existing service |

## Substitutions Format

Database substitutions are defined in the IOC configuration and processed into EPICS `.substitutions` files:

```yaml
my-ioc-01:
  type: tetramm
  environment:
    PREFIX: "XF:28ID1-ES{EM:1}"
  substitutions:
    tetramm:
      - filepath: "$(TETRAMM)/db/TetrAMM.template"
        pattern: ["P", "R", "PORT"]
        instances:
          - ["$(PREFIX)", "Ch1:", "TetrAMM"]
          - ["$(PREFIX)", "Ch2:", "TetrAMM"]
```

This generates a standard EPICS substitutions file that gets loaded via `dbLoadTemplate` during IOC startup.

## EL Version Matrix

Deployments can target multiple Enterprise Linux versions. By default, roles support EL 8 and EL 9:

```yaml
deploy_ioc_supported_el_versions: [8, 9]
```

Roles that don't support a specific EL version can override this to skip deployment on unsupported targets.
