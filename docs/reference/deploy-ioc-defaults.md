# deploy_ioc Defaults Reference

The `deploy_ioc` role provides the central deployment logic for all IOC types. Its behavior is controlled by variables defined in `roles/deploy_ioc/defaults/main.yml`, which can be overridden by device role vars, device role defaults, or the calling playbook.

## Directory Configuration

### `deploy_ioc_base_directory`

- **Type**: string
- **Default**: `"/epics"`
- **Description**: Top-level directory for all EPICS-related files. All IOC directories, common files, and module installations live under this path.

### `deploy_ioc_common_directory`

- **Type**: string
- **Default**: `"{{ deploy_ioc_base_directory }}/common"`
- **Description**: Directory for common EPICS files shared across all IOCs on a host, such as the network setup command file.

### `deploy_ioc_iocs_directory`

- **Type**: string
- **Default**: `"{{ deploy_ioc_base_directory }}/iocs"`
- **Description**: Parent directory containing all deployed IOC instance directories.

### `deploy_ioc_ioc_directory`

- **Type**: string
- **Default**: `"{{ deploy_ioc_iocs_directory }}/{{ deploy_ioc_ioc_name }}"`
- **Description**: Full path to the specific IOC being deployed. Automatically constructed from the IOCs directory and the IOC name.

### `deploy_ioc_as_dir_name`

- **Type**: string
- **Default**: `"as"`
- **Description**: Name of the autosave subdirectory within the IOC directory. Some roles (like `adaravis`) override this to `"autosave"`.

### `deploy_ioc_as_directory`

- **Type**: string
- **Default**: `"{{ deploy_ioc_ioc_directory }}/{{ deploy_ioc_as_dir_name }}"`
- **Description**: Full path to the autosave directory. Contains `req/` (request files) and `save/` (saved PV values) subdirectories.

## IOC Executable Configuration

### `deploy_ioc_template_root_path`

- **Type**: string
- **Default**: `"/usr/lib/epics"`
- **Description**: Root path for EPICS module templates and executables. Device roles typically override this to point to their compiled module path using `"{{ deploy_ioc_required_module_path }}"`.

### `deploy_ioc_executable`

- **Type**: string
- **Default**: `"softIoc"`
- **Description**: Name of the IOC executable binary. Device roles must override this to match their compiled application (e.g., `"ADAravisApp"`, `"TetrAMMApp"`, `"baseSoftIOC"`).

## Startup Script Configuration

### `deploy_ioc_standard_st_cmd`

- **Type**: boolean
- **Default**: `true`
- **Description**: Controls whether the standard st.cmd template system is used. When `true`, generates: `epicsEnv.cmd`, `base.cmd` (from device role), `common.cmd`, `postInit.cmd`, and a wrapper `st.cmd`. Set to `false` for IOCs with entirely custom startup procedures (e.g., Python-based IOCs).

### `deploy_ioc_use_common`

- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to generate and source `common.cmd` during startup. The common script loads frequently-used modules (iocStats, autosave, reccaster) and configures autosave passes. Set to `false` for IOCs that manage all their own module loading.

### `deploy_ioc_use_ad_common`

- **Type**: boolean
- **Default**: `false`
- **Description**: Whether to include Area Detector common configuration in the startup. When `true`, `common.cmd` includes AD plugin loading, NDArray pool configuration, and standard AD databases. **Must be `true` for all areaDetector-based IOCs.**

### `deploy_ioc_load_as_substitutions`

- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to process the `substitutions` field from the IOC configuration and generate `.substitutions` files loaded via `dbLoadTemplate`. Set to `false` if the device role handles database loading entirely through its own `base.cmd` template.

## Post-Deployment Behavior

### `deploy_ioc_post_deploy_step`

- **Type**: string
- **Default**: `"None"`
- **Description**: Action to take after deploying IOC files.

| Value | Effect |
|-------|--------|
| `"None"` | Only deploy files; don't touch systemd services |
| `"Install"` | Create the systemd service unit file |
| `"Install and Enable"` | Install + enable for auto-start on boot |
| `"Install and Start"` | Install + start immediately |
| `"Install and Enable and Start"` | Install + enable + start |
| `"Restart"` | Stop existing service, deploy, then restart |

### `deploy_ioc_nextport`

- **Type**: integer
- **Default**: `4000`
- **Description**: Starting port number for procServ telnet access. Each IOC on a host gets an incrementing port number for remote console access.

## Autosave Configuration

### `deploy_ioc_make_autosave_files`

- **Type**: boolean
- **Default**: `false`
- **Description**: When `true`, calls `makeAutosaveFilesFromDbInfo()` at IOC startup to automatically generate autosave request files from database info fields.

### `deploy_ioc_req_file_list`

- **Type**: list
- **Default**: `[]`
- **Description**: List of autosave request files to load. Each entry is a dict with `name` and optional `macros` fields.

Example:
```yaml
deploy_ioc_req_file_list:
  - name: auto_settings.req
    macros: "P=$(PREFIX)"
```

## Database Configuration

### `deploy_ioc_dbpf_list`

- **Type**: list
- **Default**: `[]`
- **Description**: List of `dbpf` (database put field) commands executed after `iocInit()`. Each entry specifies a PV name and value.

Example:
```yaml
deploy_ioc_dbpf_list:
  - pv: "$(PREFIX)AcquireMode"
    value: 2
    sleep: 1.0  # optional delay before executing
```

## Environment Variables

### `deploy_ioc_os_env_exports`

- **Type**: dict
- **Default**: `{}`
- **Description**: OS-level environment variables exported before the IOC process starts. Used for system configuration that isn't part of the EPICS environment (e.g., `LD_LIBRARY_PATH`).

### `deploy_ioc_device_specific_env`

- **Type**: dict
- **Default**: `{}`
- **Description**: Device-specific EPICS environment variables. Set by device role vars files to provide hardware-specific settings (port names, queue sizes, buffer counts, etc.). Merged with `deploy_ioc_default_env`.

### `deploy_ioc_default_env`

- **Type**: dict
- **Default**: See below
- **Description**: Base set of EPICS environment variables available to all IOCs. Provides paths to standard EPICS modules and IOC identity variables.

```yaml
deploy_ioc_default_env:
  IOC: "{{ ioc.type }}"
  IOC_DIR: "{{ deploy_ioc_iocs_directory }}"
  TOP: "$(IOC_DIR)/{{ deploy_ioc_ioc_name }}"
  TEMPLATE_TOP: "{{ deploy_ioc_template_root_path }}"
  HOSTNAME: "{{ inventory_hostname.split('.')[0] }}"
  IOCNAME: "{{ deploy_ioc_ioc_name }}"
  ASYN: /usr/lib/epics
  AUTOSAVE: /usr/lib/epics
  BUSY: /usr/lib/epics
  CALC: /usr/lib/epics
  DEVIOCSTATS: /usr/lib/epics
  SSCAN: /usr/lib/epics
  STREAM: /usr/lib/epics
  SNCSEQ: /usr/lib/epics
  RECCASTER: /usr/lib/epics
  EPICS_BASE: /usr/lib/epics
```

!!! note
    Module paths default to `/usr/lib/epics` because the standard `epics-bundle` RPM installs everything there. When a device role compiles its own module, it overrides `deploy_ioc_template_root_path` to point to the compiled module location.

## System Packages

### `deploy_ioc_required_system_packages`

- **Type**: list
- **Default**: `["procServ"]`
- **Description**: System packages installed via `dnf` before IOC deployment. `procServ` is required for managing IOC processes with telnet console access. Device roles can extend this list with additional packages.

## Python IOC Configuration

### `deploy_ioc_pixi_executable_path`

- **Type**: string
- **Default**: `"pixi"`
- **Description**: Path to the `pixi` executable on the target machine. Used by Python-based IOC roles to initialize virtual environments.

## EL Version Support

### `deploy_ioc_supported_el_versions`

- **Type**: list
- **Default**: `[8, 9]`
- **Description**: List of supported Enterprise Linux major versions. Roles that depend on packages not available on certain EL versions can restrict deployment by overriding this variable.

## Manual IOC Files

### `deploy_ioc_manual_ioc_files`

- **Type**: dict
- **Default**: `{}` (commented out)
- **Description**: A dict mapping filenames to their content for manually-placed IOC files. Files are placed based on extension:

| Extension | Destination Directory |
|-----------|----------------------|
| `.cmd` | `iocBoot/` |
| `.req` | `<autosave_dir>/req/` |
| `.db`, `.template`, `.substitutions` | `db/` |

Example:
```yaml
deploy_ioc_manual_ioc_files:
  custom_setup.cmd: |
    # Custom commands
    dbLoadRecords("custom.db", "P=$(PREFIX)")
  custom.req: |
    file custom_settings.req P=$(PREFIX)
```
