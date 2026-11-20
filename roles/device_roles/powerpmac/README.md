# powerpmac

Deploys a motor IOC for a Delta Tau / Omron Power PMAC motion controller, communicating over SSH, with optional coordinate systems and virtual axes. The IOC is built from [ppmac](https://github.com/NSLS2/ppmac) (version `91b4edc`).

## Example Configuration

Taken from [`examples/mc91/config.yml`](examples/mc91/config.yml) (see also [`examples/mc92/config.yml`](examples/mc92/config.yml) for `disable_all_limits`/`poll_periods`, and [`examples/mc93/config.yml`](examples/mc93/config.yml) for a minimal single-axis setup):

```yaml
mc91:
  type: powerpmac
  environment:
    SYS: "XF:31ID1-OP:1"
    CONTROLLER: "MC:01"
    DEV: "{$(CONTROLLER)}"
    CT_SYS: "XF:31ID1-CT"
    NUM_AXES: 8 # Controller has 8 axes, even though only 4 are used
    ENGINEER: "J. Wlodek"
    MOVING_POLL_PERIOD: 100
    IDLE_POLL_PERIOD: 1000
    CONTROLLER_IP: "xf31id1-lab3-mc1.nsls2.bnl.local"

  disable_all_limits: false # Defaults to false. If true all limits are disabled

  # Define a coordinate system
  coord_systems:
    - num: 2
      motion_prog: 10
      num_axes: 9

  # Note: if mres uses exponential notation, include a decimal point and at least one digit after it (e.g., 5.0e-5) so it parses as a number.
  axes:
    - name: "Rot"
      num: 1
      component: CMT:1
      desc: "Rotation"
      mres: 0.045
      egu: "deg"
      disable_limits: true

    - name: "X"
      num: 2
      component: CMT:1
      desc: "X translation"
      mres: 5.0e-5
      egu: "mm"

    - name: "Y"
      num: 3
      component: CMT:1
      desc: "Y translation"
      mres: 5.0e-5
      egu: "mm"

    - name: "Z"
      num: 4
      component: CMT:1
      desc: "Z translation"
      mres: 5.0e-5
      egu: "mm"

  virtual_axes:
    - name: "Diag"
      num: 7
      cs: 2
      component: CMT:1
      desc: "X-Y Diagonal translation virtual axis"
      mres: 0.00001
      egu: "mm"
      home_plc: 17  # Optional
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `powerpmac`. |
| `environment.ENGINEER` | No | - | Name/contact of the responsible engineer. |
| `environment.SYS` | Yes | - | System prefix for motor PVs; motors are named `<SYS>{<component>-Ax:<name>}`. |
| `environment.CONTROLLER` | Yes | - | Controller name (e.g. `MC:01`). Used in `CT_PREFIX`/`IOC_PREFIX`, the `ppmacStatus.db` records and the per-axis status PVs (`{<CONTROLLER>-Ax:<num>}`). |
| `environment.DEV` | Yes | - | Device portion (typically `{$(CONTROLLER)}`); `asynComm.db` is loaded with `P=$(CT_SYS)$(DEV)`. |
| `environment.CT_SYS` | Yes | - | Controls system prefix for controller/status PVs. |
| `environment.NUM_AXES` | Yes | - | Number of axes on the controller (1-16), passed to `pmacCreateController`/`pmacCreateAxes`. |
| `environment.MOVING_POLL_PERIOD` | No | `100` | Moving poll period (ms) for `pmacCreateController`. |
| `environment.IDLE_POLL_PERIOD` | No | `1000` | Idle poll period (ms) for `pmacCreateController`. |
| `environment.CONTROLLER_IP` | Yes | - | IP address or hostname of the Power PMAC. |
| `environment.CTRL_PORT` | No | `M0` | Controller (motor record) asyn port name. |
| `environment.SSH_PORT` | No | `P0` | Low-level SSH asyn port name. |
| `environment.CT_PREFIX` | No | `$(CT_SYS){$(CONTROLLER)}` | Prefix for autosave status and reccaster PVs. |
| `environment.IOC_PREFIX` | No | `$(CT_SYS){IOC-$(CONTROLLER)}` | Prefix for iocStats PVs. |
| `disable_all_limits` | No | `false` | If true, disables the limits check for all axes (per-axis `disable_limits` is then ignored). |
| `coord_systems` | No | - | List of coordinate systems to create. |
| `coord_systems[].num` | Yes | - | Coordinate system number; asyn port is `CS<num>`. |
| `coord_systems[].motion_prog` | Yes | - | Motion program number (1-99). |
| `coord_systems[].num_axes` | Yes | - | Number of CS axes passed to `pmacCreateCSAxes`. |
| `axes` | No* | - | List (1-16) of real motor axes. |
| `axes[].name` | Yes | - | Axis name used in the PV (`-Ax:<name>`). |
| `axes[].num` | Yes | - | Axis number on the controller (1-16). |
| `axes[].component` | Yes | - | Component name used in the PV (`{<component>-Ax:<name>}`). |
| `axes[].desc` | Yes | - | Motor description (`DESC`). |
| `axes[].mres` | Yes | - | Motor resolution. If written in exponential notation, include a decimal point (e.g. `5.0e-5`) so it parses as a number. |
| `axes[].egu` | Yes | - | Engineering units. |
| `axes[].disable_limits` | No | `false` | If true, disables the limits check for this axis. |
| `axes[].home_plc` | No | `num + 7` | PLC number used for auto-homing (1-30). |
| `virtual_axes` | No | - | List of coordinate-system (virtual) axes. |
| `virtual_axes[].name` | Yes | - | Axis name used in the PV. |
| `virtual_axes[].num` | Yes | - | CS axis number (1-16). |
| `virtual_axes[].cs` | Yes | - | Coordinate system number the axis belongs to. |
| `virtual_axes[].component` | Yes | - | Component name used in the PV. |
| `virtual_axes[].desc` | Yes | - | Motor description. |
| `virtual_axes[].mres` | Yes | - | Resolution; `1/mres` is used as the CS steps per unit. |
| `virtual_axes[].egu` | Yes | - | Engineering units. |
| `virtual_axes[].home_plc` | No | - | Auto-home PLC number (1-30); only added to `autohome.substitutions` if set. |
| `poll_periods` | No | - | List of poll period overrides (`card` 1-4, `idle`, `moving`, `cs`). |

## Notes

- Generates `iocBoot/base.cmd` plus `db/motor.substitutions`, `db/motorstatus.substitutions`, `db/pmacStatus.substitutions`, `db/autohome.substitutions`, and `db/cs.substitutions` (only when `virtual_axes` is defined; also loads `motor_in_cs.template` for all real axes).
- The SSH connection uses the default Power PMAC credentials (`root`/`deltatau`), hard-coded in `base.cmd`.
- `pmacSetCoordStepsPerUnit` for virtual axes is only emitted when `coord_systems` is also defined.
- Inconsistencies: `poll_periods` is in the schema and the `mc92` example but is not used by any template. `axes` is optional in the schema, but the templates iterate over it unconditionally, so it is effectively required.
