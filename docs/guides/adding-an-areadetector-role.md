# Adding an areaDetector Role

areaDetector-based IOCs follow a specific pattern that differs from standard EPICS IOCs. This guide covers the additional requirements and conventions for AD roles.

## areaDetector Architecture

An areaDetector IOC typically consists of:

```
ADSupport → ADCore → ADGenICam (optional) → AD<Driver>
```

Each layer is a separate installable module with its own vars file. The `install_module` role handles the full dependency chain automatically.

## Key Differences from Standard Roles

| Aspect | Standard Role | AD Role |
|--------|--------------|---------|
| `deploy_ioc_use_ad_common` | `false` | **`true`** |
| Module dependencies | Few or none | Chain: ADSupport → ADCore → driver |
| `include_base_ad_config` | N/A | `true` in module vars |
| Template root | Module root | `<module>/iocs/<iocApp>` |
| Environment variables | Minimal | Port, queue sizes, buffer counts, etc. |
| Autosave | Optional | Usually required |

## Step-by-Step Guide

### Step 1: Create the Module Chain

Most AD drivers depend on ADCore (which depends on ADSupport). If these already exist in `roles/install_module/vars/`, you can reference them directly.

For a new driver, create `roles/install_module/vars/mydriver_abc1234.yml`:

```yaml
---

mydriver_abc1234:
  name: MyDriver
  url: https://github.com/areaDetector/MyDriver
  include_base_ad_config: true
  version: abc1234
  executable: MyDriverApp
  module_deps:
    - adcore_60080dc
```

!!! note
    Setting `include_base_ad_config: true` automatically includes the full AD build configuration (HDF5, TIFF, JPEG, netCDF, etc.) via `install_module_ad_config_dict`.

If your driver uses GenICam (GigE Vision, USB3 Vision cameras):

```yaml
  module_deps:
    - adgenicam_5d08a11
```

`adgenicam` already depends on `adcore`, so transitive resolution handles the full chain.

### Step 2: Create the Vars File

Create `roles/deploy_ioc/vars/mydriver.yml`:

```yaml
---

deploy_ioc_use_ad_common: true
deploy_ioc_required_module: mydriver_abc1234
deploy_ioc_template_root_path:
  "{{ deploy_ioc_required_module_path }}/iocs/myDriverIOC"
deploy_ioc_req_file_list:
  - name: auto_settings.req
    macros: "P=$(PREFIX)"
deploy_ioc_device_specific_env:
  PORT: "DRV1"
  QSIZE: 20
  NCHANS: 2048
  CBUFFS: 500
  MAX_THREADS: 8
  EPICS_DB_INCLUDE_PATH: "$(ADCORE)/db"
```

Key points:

- **`deploy_ioc_use_ad_common: true`** — Loads standard AD plugins (file plugins, stats, ROI, etc.)
- **`deploy_ioc_template_root_path`** — Points to the IOC application within the compiled module. AD modules typically have IOCs under `iocs/<name>IOC/`.
- **`deploy_ioc_req_file_list`** — AD IOCs almost always need autosave for camera settings
- **`EPICS_DB_INCLUDE_PATH`** — Helps EPICS find database files across modules

### Standard AD Environment Variables

Most AD roles should include these environment variables:

| Variable | Typical Value | Purpose |
|----------|---------------|---------|
| `PORT` | `"DRV1"` | Asyn port name for the driver |
| `QSIZE` | `20` | Queue size for plugin chain |
| `NCHANS` | `2048` | Number of channels for MCA/spectrum |
| `CBUFFS` | `500` | Circular buffer count |
| `MAX_THREADS` | `8` | Maximum processing threads |
| `EPICS_DB_INCLUDE_PATH` | `"$(ADCORE)/db"` | Database file search path |
| `NELEMENTS` | `500000` | Max array elements (for large images, increase) |

### Step 3: Create the Schema

Create `roles/device_roles/mydriver/schema.yml`:

```yaml
---

type: enum("mydriver")
environment:
  ENGINEER: str()
  PREFIX: str()
  # Device-specific fields
  CAMERA_IP: ip(required=False)
  SERIAL_NUMBER: str(required=False)
```

### Step 4: Create the base.cmd Template

Create `roles/device_roles/mydriver/templates/base.cmd.j2`:

```jinja2
# Load the driver database definitions
dbLoadDatabase("{{ deploy_ioc_template_root_path }}/dbd/{{ deploy_ioc_executable }}.dbd")
{{ deploy_ioc_executable }}_registerRecordDeviceDriver(pdbbase)

# Configure the driver
# MyDriverConfig(portName, param1, param2, maxBuffers, maxMemory)
MyDriverConfig("$(PORT)", "{{ ioc.environment.CAMERA_IP | default('') }}", 0, 0)

# Load driver-specific database
dbLoadRecords("$(TEMPLATE_TOP)/db/MyDriver.template", "P=$(PREFIX),R=cam1:,PORT=$(PORT),ADDR=0,TIMEOUT=1")
```

### Step 5: Create the Autosave Request Template

Create `roles/device_roles/mydriver/templates/auto_settings.req.j2`:

```jinja2
file MyDriver_settings.req P=$(P)
file commonPlugin_settings.req P=$(P)
```

### Step 6: Create the Tasks

Create `roles/device_roles/mydriver/tasks/main.yml`:

```yaml
---
# Tasks for mydriver role

- name: Install base.cmd
  ansible.builtin.template:
    src: "templates/base.cmd.j2"
    dest: "{{ deploy_ioc_ioc_directory }}/iocBoot/base.cmd"
    owner: "{{ host_config.softioc_user }}"
    group: "{{ host_config.softioc_group }}"
    mode: "0664"

- name: Copy autosave req file
  ansible.builtin.template:
    src: "templates/auto_settings.req.j2"
    dest: "{{ deploy_ioc_as_directory }}/req/auto_settings.req"
    owner: "{{ host_config.softioc_user }}"
    group: "{{ host_config.softioc_group }}"
    mode: "0664"
```

### Step 7: Create the Example

Create `roles/device_roles/mydriver/example.yml`:

```yaml
---

mydriver-01:
  type: mydriver
  environment:
    ENGINEER: "C. Engineer"
    PREFIX: "XF:31ID1-ES{Cam:1}"
    CAMERA_IP: "10.0.0.100"
```

## Real-World Example: ADAravis

The `adaravis` role is a complete example of an AD role with extra complexity (camera model detection via `arv-tool`).

### Module vars (`roles/install_module/vars/adaravis_a0aa4d6.yml`)

```yaml
adaravis_a0aa4d6:
  name: ADAravis
  url: https://github.com/areaDetector/ADAravis
  include_base_ad_config: true
  version: a0aa4d6
  executable: ADAravisApp
  module_deps:
    - adgenicam_5d08a11
```

### Deploy vars (`roles/deploy_ioc/vars/adaravis.yml`)

```yaml
deploy_ioc_use_ad_common: true
deploy_ioc_required_module: adaravis_a0aa4d6
deploy_ioc_template_root_path:
  "{{ deploy_ioc_required_module_path }}/iocs/aravisIOC"
deploy_ioc_as_dir_name: autosave
deploy_ioc_req_file_list:
  - name: auto_settings.req
    macros: "P=$(PREFIX)"
deploy_ioc_device_specific_env:
  PORT: "ARV1"
  QSIZE: 20
  NCHANS: 2048
  CBUFFS: 500
  MAX_THREADS: 8
  EPICS_DB_INCLUDE_PATH: "$(ADCORE)/db:$(ADGENICAM)/db:$(ADARAVIS)/db"
  NELEMENTS: 500000
```

### Tasks (`roles/device_roles/adaravis/tasks/main.yml`)

```yaml
- name: Ensure aravis rpm package is installed
  ansible.builtin.dnf:
    name: aravis
    state: present

- name: Get camera model information
  ansible.builtin.shell: >-
    set -o pipefail;
    arv-tool -n "{{ ioc.environment.CAMERA_NAME }}"
    control DeviceModelName |
    sed 's/DeviceModelName = //g' |
    sed 's/ /_/g'
  args:
    executable: /bin/bash
  register: adaravis_arv_tool_model_output
  changed_when: false

- name: Set camera model name
  ansible.builtin.set_fact:
    adaravis_camera_model_name: "{{ adaravis_arv_tool_model_output.stdout }}"

- name: Auto generate feature databases and bob screens
  ansible.builtin.include_tasks: autogen_files.yml

- name: Install base startup script
  ansible.builtin.template:
    src: "templates/base.cmd.j2"
    dest: "{{ deploy_ioc_ioc_directory }}/iocBoot/base.cmd"
    owner: "{{ host_config.softioc_user }}"
    group: "{{ host_config.softioc_group }}"
    mode: "0664"

- name: Copy autosave req file
  ansible.builtin.template:
    src: "templates/auto_settings.req.j2"
    dest: "{{ deploy_ioc_as_directory }}/req/auto_settings.req"
    owner: "{{ host_config.softioc_user }}"
    group: "{{ host_config.softioc_group }}"
    mode: "0664"
```

Note how `adaravis` extends the standard pattern with:

- Installing system packages (`aravis` RPM)
- Querying hardware information (`arv-tool`)
- Auto-generating files based on the detected camera model

## Real-World Example: ADSimDetector

`adsimdetector` is the simplest AD role — no hardware interaction, just configuration:

### Deploy vars (`roles/deploy_ioc/vars/adsimdetector.yml`)

```yaml
deploy_ioc_template_root_path:
  "{{ deploy_ioc_required_module_path }}/iocs/simDetectorIOC"
deploy_ioc_required_module: adsimdetector_4b236f4
deploy_ioc_use_ad_common: true
deploy_ioc_req_file_list:
  - name: auto_settings.req
    macros: "P=$(PREFIX)"
deploy_ioc_device_specific_env:
  PORT: "SIM1"
  QSIZE: 20
  NCHANS: 2048
  CBUFFS: 500
  MAX_THREADS: 8
  XSIZE: 1024
  YSIZE: 1024
  EPICS_DB_INCLUDE_PATH: "$(ADCORE)/db"
```

### Schema (`roles/device_roles/adsimdetector/schema.yml`)

```yaml
type: enum("adsimdetector")
environment:
  PREFIX: str()
  XSIZE: int(min=1)
  YSIZE: int(min=1)
  FFMSTREAM_PORT: int(min=8000, required=False)
```

## Tips for AD Roles

1. **Check existing AD roles first** — Browse `roles/device_roles/ad*` for similar implementations.
2. **Use `EPICS_DB_INCLUDE_PATH`** — Include paths to all modules that provide `.db`/`.template` files.
3. **Always include autosave** — AD IOCs have many configurable PVs that should persist across restarts.
4. **Test with ADSimDetector first** — If unsure, model your role after `adsimdetector` and add complexity incrementally.
5. **Handle missing hardware gracefully** — For roles that query hardware (like `adaravis`), ensure CI can still test deployment structure even without real hardware (see `skip_compilation` in verify.yml).
