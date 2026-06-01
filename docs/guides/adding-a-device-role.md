# Adding a New Device Role

A device role defines how to deploy a specific type of EPICS IOC. Each role customizes the deployment for its hardware by providing device-specific templates, environment variables, and startup commands.

## When to Add a Device Role

Add a device role when you have a new IOC type that:

- Needs a specific EPICS module compiled from source
- Requires custom startup commands beyond the standard template
- Has hardware-specific environment variables or configuration

## Interactive Method (Recommended)

```bash
pixi run make-role
```

This prompts you for:

1. **Role name** — Lowercase identifier (e.g., `sr570`, `tetramm`)
2. **Standard st.cmd?** — Whether to use the standard startup script system
3. **Use common.cmd?** — Whether to include common module loading
4. **areaDetector?** — Whether this is an AD-based IOC
5. **Required module** — Select from existing modules or create a new one
6. **Executable name** — The IOC binary name from the compiled module

The script creates all necessary files and directories.

## What Gets Created

After running `make-role` for a role named `mydevice`:

```
roles/
├── deploy_ioc/
│   └── vars/
│       └── mydevice.yml          # Variable overrides for this IOC type
└── device_roles/
    └── mydevice/
        ├── README.md             # Documentation
        ├── example.yml           # Working example configuration
        ├── schema.yml            # Input validation schema
        ├── tasks/
        │   └── main.yml          # Device-specific Ansible tasks
        └── templates/
            └── base.cmd.j2       # Device-specific startup commands
```

## Manual Method

### Step 1: Create the Vars File

Create `roles/deploy_ioc/vars/mydevice.yml`:

```yaml
---

deploy_ioc_required_module: mymodule_abc1234
deploy_ioc_executable: myModuleApp
deploy_ioc_template_root_path: "{{ deploy_ioc_required_module_path }}"
deploy_ioc_use_common: true
deploy_ioc_use_ad_common: false
deploy_ioc_device_specific_env:
  PORT: "MY_PORT"
  CUSTOM_VAR: "value"
```

Key variables to set:

| Variable | Purpose |
|----------|---------|
| `deploy_ioc_required_module` | Module config name to compile |
| `deploy_ioc_executable` | IOC binary executable name |
| `deploy_ioc_template_root_path` | Where to find the IOC application |
| `deploy_ioc_use_common` | Include common.cmd in startup |
| `deploy_ioc_use_ad_common` | Include AD common config |
| `deploy_ioc_device_specific_env` | Extra environment variables |

### Step 2: Create the Device Role Directory

```bash
mkdir -p roles/device_roles/mydevice/{tasks,templates}
```

### Step 3: Create the Schema

Create `roles/device_roles/mydevice/schema.yml`:

```yaml
---

type: enum("mydevice")
environment:
  ENGINEER: str()
  PREFIX: str()
  MY_SETTING: int(min=0, max=100)
  OPTIONAL_FIELD: str(required=False)
```

The schema uses [yamale](https://github.com/23andMe/Yamale) syntax. Common validators:

| Validator | Description |
|-----------|-------------|
| `str()` | Any string |
| `int()` | Integer |
| `int(min=0, max=10)` | Bounded integer |
| `num()` | Number (int or float) |
| `bool()` | Boolean |
| `enum("a", "b")` | One of specified values |
| `ip()` | IP address |
| `any(str(), int())` | Multiple allowed types |

Add `required=False` for optional fields, `default=X` for defaults.

### Step 4: Create the Example Configuration

Create `roles/device_roles/mydevice/example.yml`:

```yaml
---

mydevice-01:
  type: mydevice
  environment:
    ENGINEER: "C. Engineer"
    PREFIX: "XF:31ID1-ES{MYDEVICE:01}"
    MY_SETTING: 50
```

!!! important
    The example must be a valid configuration that passes schema validation. It is tested in CI.

### Step 5: Create the Tasks

Create `roles/device_roles/mydevice/tasks/main.yml`:

```yaml
---
# Tasks for mydevice role

- name: Install base.cmd
  ansible.builtin.template:
    src: templates/base.cmd.j2
    dest: "{{ deploy_ioc_ioc_directory }}/iocBoot/base.cmd"
    mode: "0664"
    owner: "{{ host_config.softioc_user }}"
    group: "{{ host_config.softioc_group }}"
```

### Step 6: Create the base.cmd Template

Create `roles/device_roles/mydevice/templates/base.cmd.j2`:

```jinja2
dbLoadDatabase("{{ deploy_ioc_template_root_path }}/dbd/{{ deploy_ioc_executable }}.dbd")
{{ deploy_ioc_executable }}_registerRecordDeviceDriver(pdbbase)

# Device-specific initialization
myDeviceConfigure("$(PORT)", "$(MY_SETTING)")

# Load databases
dbLoadRecords("$(TEMPLATE_TOP)/db/myDevice.template", "P=$(PREFIX),PORT=$(PORT)")
```

### Step 7 (Optional): Create Additional Templates

If your device needs autosave request files, additional command files, or other templates, add them to `templates/` and reference them from your tasks.

## Validation Checklist

After creating your role, verify:

- [ ] `pixi run tests tests/test_device_roles.py` passes (vars file exists)
- [ ] `pixi run tests tests/test_deploy_ioc_vars.py` passes (vars file valid)
- [ ] `pixi run tests tests/test_validate_ex_configs_against_schemas.py` passes (example matches schema)
- [ ] Local deployment works: `pixi run deployment -t mydevice --container -m 8`

## Role Structure Best Practices

1. **Keep tasks minimal** — Only add device-specific steps. The core `deploy_ioc` role handles standard operations.
2. **Use the templating system** — Put device-specific startup commands in `templates/base.cmd.j2`.
3. **Document environment variables** — Include comments in your schema explaining what each variable does.
4. **Provide a realistic example** — The example should work out-of-the-box for local testing (even if it requires a simulated device).
5. **Pin module versions** — Always use git commit hashes, never branches or moving tags.

## Deleting a Role

```bash
pixi run delete-role
```

This removes the device role directory and its vars file.
