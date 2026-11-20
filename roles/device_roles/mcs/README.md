# mcs

Deploys a motor IOC for SmarAct MCS piezo positioner controllers over Ethernet, supporting both the original MCS (`model: 1`) and MCS2 (`model: 2`) controllers. The IOC is built from [mcs-ioc](https://github.com/NSLS2/mcs-ioc) (version `49f0f2b`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
mcs2-01:
  type: mcs
  model: 2
  environment:
    PORT: "MCS2"
    CTRL_NAME: "MCS2:01"
    CTRL_IP: "127.0.0.1"
    P: "XF31ID1-ES"
    R: "{$(CTRL_NAME)}"
    NUM_AXES: 6 # Standard MCS2 benchtop controller has 2x3 axes
    # Use a bitmask to specify which axes are used. 1 = unused, 0 = used.
    # This example only uses axis 4, so the mask for a 6-axis controller
    # is 110111 = 0x37
    AXES_MASK: 0x37
    ENGINEER: C. Engineer

  # Define the individal motor axes here
  axes:
    - name: "X"
      num: 4
      desc: "X"
      mres: 0.00001
      egu: "mm"
      dir: "Pos"
      velo: 2.0

  substitutions:
    asynComm:
      - filepath: "$(ASYN)/db/asynRecord.db"
        pattern: ["P", "R", "ADDR", "PORT", "TIMEOUT", "IMAX", "OMAX"]
        instances:
          - ["$(P)", "$(R)AsynIO", "$(PORT)", "1", "0", "256", "256"]
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `mcs`. |
| `model` | Yes | - | Controller model: `1` (MCS, `smarActMCSCreateController`) or `2` (MCS2, `MCS2CreateController`). Also selects the substitutions file name `db/mcs<model>.substitutions`. |
| `simulation` | No | `false` | Simulation flag (generic deploy_ioc option); not used by this role's templates. Use `CTRL_PORT_NUM` to point at a simulator. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.CTRL_NAME` | Yes | - | Controller name; axis PVs are `$(P){<CTRL_NAME>-Ax:<axis name>}Mtr`. |
| `environment.CTRL_IP` | Yes | - | IP address or hostname of the controller. |
| `environment.CTRL_PORT_NUM` | No | `55551` (model 2), `5000` (model 1) | Controller TCP port; only set if different from the default (e.g. for simulation). |
| `environment.P` | Yes | - | PV prefix for the motor records. |
| `environment.R` | Yes | - | Second part of the IOC prefix; `PREFIX` defaults to `$(P)$(R)`. |
| `environment.AXES_MASK` | Yes | - | Bitmask of axes to skip (bit = 1 means unused, 0 means used), passed to the controller create function. |
| `environment.PORT` | Yes | `MCS2` | asyn port name of the motor controller; the underlying IP port is `<PORT>_ETH`. |
| `environment.NUM_AXES` | Yes | - | Number of axes on the controller (min 1). For model 1, `smarActMCSCreateAxis` is called for axes `0..NUM_AXES-1`. |
| `environment.PREFIX` | No | `$(P)$(R)` | IOC prefix for iocAdmin, autosave status and reccaster records. |
| `environment.MOVING_POLL_PERIOD` | No | `50` | Moving poll period (ms). |
| `environment.IDLE_POLL_PERIOD` | No | `1000` | Idle poll period (ms). |
| `environment.DISABLE_SPEED` | No | `0` | Set in the IOC environment; not used by this role's templates. |
| `axes` | Yes | - | List (at least one) of motor axes; each creates a `$(MCS)/db/motor.db` instance (and, for model 2, an `MCS2_Extra.db` instance). |
| `axes[].name` | Yes | - | Axis name, used in the PV name and as the motor `ALIAS`. |
| `axes[].num` | Yes | - | 1-based axis number on the controller; the asyn address is `num - 1`. |
| `axes[].desc` | Yes | - | Motor record description (`DESC`). |
| `axes[].mres` | Yes | - | Motor resolution (`MRES`). |
| `axes[].egu` | Yes | - | Engineering units (`EGU`); the template falls back to `mm` if omitted. |
| `axes[].dir` | No | `Pos` | Direction, `Pos` or `Neg`. |
| `axes[].velo` | No | `2.0` | Velocity (`VELO`). |
| `axes[].accl` | No | `0.2` | Acceleration time (`ACCL`). |
| `axes[].vmax` | No | `5.0` | Maximum velocity (`VMAX`). |
| `axes[].prec` | No | `5` | Display precision (`PREC`). |
| `substitutions` | No | - | Generic deploy_ioc option for loading extra databases (not part of this role's schema); used in the example to load an `asynRecord`. |

## Notes

- Generates `iocBoot/base.cmd` (creates `<PORT>_ETH` IP port to `CTRL_IP:CTRL_PORT_NUM` and the controller) and `db/mcs<model>.substitutions`. `VBAS`, `BDST`, `DHLM` and `DLLM` are fixed at `0`; `BVEL`/`BACC` at `0.5`.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- In the example's `asynComm` substitution, the instance values for `ADDR` and `PORT` appear swapped relative to the `pattern` (`ADDR="$(PORT)"`, `PORT="1"`).
