# turbopmac

Deploys a motor IOC for a Delta Tau Turbo PMAC motion controller over TCP/IP, with optional open-loop axes, coordinate systems and virtual axes. The IOC is built from [tpmac](https://github.com/NSLS2/tpmac) (version `44274d1`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
mc01:
  type: turbopmac
  environment:
    ENGINEER: J. Wlodek
    SYS: "XF:31ID1-ES"
    PMAC: "MC:01"
    DEV: "{$(PMAC)}"
    CT_SYS: XF:31ID1-CT
    IOC_ASYN: "$(CT_SYS)$(DEV)Asyn"
    ASYN_PORT: "P0"
    CONTROLLER_PORT: "M0"
    NUM_AXES: 8
    CONTROLLER_IP: "10.10.10.10"

  disable_all_limits: false # Disable limits for all axes
  disable_lim_axes: [1, 4] # Disable limits for axes 1 and 4

  # Define open loop axes
  open_loop_axes:
    - axis_num: 1
      encoder_axis: 1
    - axis_num: 2
      encoder_axis: 5

  # Define coordinate systems
  coord_systems:
    - num: 2
      motion_prog: 10
      num_axes: 9

  # Define axes
  axes:
    - name: "Rot"
      num: 1
      component: Smpl:Trans
      desc: "Rotation"
      mres: 0.0001
      egu: "deg"
      home_plc: 8

    - name: "X"
      num: 2
      component: Smpl:Trans
      desc: "X translation"
      mres: 0.0001
      egu: "mm"
      home_plc: 9

    - name: "Y"
      num: 3
      component: Smpl:Trans
      desc: "Y translation"
      mres: 0.0001
      egu: "mm"
      home_plc: 10

    - name: "Z"
      num: 4
      component: Smpl:Trans
      desc: "Z translation"
      mres: 0.0001
      egu: "mm"
      home_plc: 11

# Define virtual axes
virtual_axes:
  - name: "Diag"
    num: 7
    cs: 2
    component: Smpl:Trans
    desc: "X-Y diagonal translation virtual axis"
    mres: 0.0001
    egu: "mm"
    home_plc: 17
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `turbopmac`. |
| `environment.ENGINEER` | No | - | Name/contact of the responsible engineer. |
| `environment.SYS` | Yes | - | System prefix for motor PVs (`<SYS>{<component>-Ax:<name>}`). |
| `environment.DEV` | Yes | - | Device portion (typically `{$(PMAC)}`); used for the `asynComm.db` prefix when `IOC_ASYN` is not set. |
| `environment.PMAC` | Yes | - | Controller name (e.g. `MC:01`), typically referenced by `DEV`. |
| `environment.ASYN_PORT` | Yes | - | Low-level asyn IP port name (`pmacAsynIPConfigure`). |
| `environment.CONTROLLER_PORT` | Yes | - | Controller (motor record) asyn port name. |
| `environment.NUM_AXES` | Yes | - | Number of axes (1-8), passed to `pmacCreateController`/`pmacCreateAxes`. |
| `environment.CONTROLLER_IP` | Yes | - | IP address or hostname of the controller; connected to on port 1025. |
| `environment.CT_SYS` | No | - | Controls system prefix; used for `pmacStatusAxis.db` and, if `IOC_ASYN` is not set, for the asynComm prefix `<CT_SYS><DEV>Asyn` (else `<SYS><DEV>Asyn`). |
| `environment.IOC_ASYN` | No | - | Explicit prefix for the `asynComm.db` records. |
| `environment.STREAM_PROTOCOL_PATH` | No | `$(EPICS_BASE)/protocol:$(TPMAC)/protocol:$(TOP)/protocol:.` | StreamDevice protocol path. |
| `disable_all_limits` | No | - | Disables the limits check for all axes. |
| `disable_lim_axes` | No | - | List of axis numbers (1-8) whose limits check is disabled. Ignored if `disable_all_limits` is set. |
| `open_loop_axes` | No | - | List of open-loop axes. |
| `open_loop_axes[].axis_num` | Yes | - | Open-loop axis number (1-8). |
| `open_loop_axes[].encoder_axis` | Yes | - | Encoder axis (1-8) for the open-loop axis (`pmacSetOpenLoopEncoderAxis`). |
| `coord_systems` | No | - | List of coordinate systems to create. |
| `coord_systems[].num` | Yes | - | Coordinate system number; asyn motor port is `CS<num>`. |
| `coord_systems[].motion_prog` | Yes | - | Motion program number (1-99). |
| `coord_systems[].num_axes` | Yes | - | Number of axes passed to `drvAsynMotorConfigure`. |
| `axes` | Yes | - | List (1-8) of real motor axes. |
| `axes[].name` | Yes | - | Axis name used in the PV (`-Ax:<name>`). |
| `axes[].num` | Yes | - | Axis number on the controller (1-8). |
| `axes[].component` | Yes | - | Component name used in the PV (`{<component>-Ax:<name>}`). |
| `axes[].desc` | Yes | - | Motor description (`DESC`). |
| `axes[].mres` | Yes | - | Motor resolution. |
| `axes[].egu` | Yes | - | Engineering units. |
| `axes[].home_plc` | Yes | - | Homing PLC number (1-20). |
| `virtual_axes` | No | - | List of coordinate-system (virtual) axes. |
| `virtual_axes[].name` | Yes | - | Axis name. |
| `virtual_axes[].num` | Yes | - | CS axis number (1-8). |
| `virtual_axes[].cs` | Yes | - | Coordinate system number. |
| `virtual_axes[].component` | Yes | - | Component name. |
| `virtual_axes[].desc` | Yes | - | Description. |
| `virtual_axes[].mres` | Yes | - | Resolution; `1/mres` is used as the CS steps per unit. |
| `virtual_axes[].egu` | Yes | - | Engineering units. |
| `virtual_axes[].home_plc` | Yes | - | Homing PLC number (1-20). |

## Notes

- Generates `iocBoot/base.cmd` plus `db/motor.substitutions` (motors named `...Mtr`), `db/motorstatus.substitutions` (`motorstatus.db` and `pmacStatusAxis.db`) and `db/pmac_asyn_motor.substitutions`.
- Poll periods are fixed at 100 ms moving / 1000 ms idle (and 200/2000 ms for coordinate systems, if defined).
- Autosave monitors `info_positions.req` and `info_settings.req` without macros.
- Inconsistencies:
  - `disable_all_limits` is only checked for being defined, so `disable_all_limits: false` (as in the example) still disables limits on all axes and causes `disable_lim_axes` to be ignored.
  - In the example, `virtual_axes` is not indented under `mc01`, so it is not part of the IOC config.
  - `home_plc` is required by the schema but not used by any template, and virtual axes get no motor records (no CS substitutions are generated).
  - `CT_SYS` is optional in the schema but always used in `motorstatus.substitutions`.
  - No `PREFIX`/`IOC_PREFIX`/`CT_PREFIX` is defined, though the common startup uses one for the iocStats records.
