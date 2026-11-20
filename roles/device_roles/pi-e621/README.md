# pi-e621

Deploys IOCs for PI E-621 piezo motion controllers using asynchronous motor
support, connected over TCP (e.g. via a terminal server). The IOC is built from
[pi-e621-ioc](https://github.com/NSLS2/pi-e621-ioc) (version `043ec8f`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
pi-e621:
  type: "pi-e621"

  environment:
    HOST: "xf09id1-tsrv6.nsls2.bnl.gov:4001"
    PI_PORT: "PI_VMS"
    SYS: "XF:09IDA-OP:1"
    IOC_SYS: "XF:09IDA-CT"
    IOC_DEV: "IOC:PZT3"
    ASYN_DEV: "MC:PZT3"
    IOC_PREFIX: $(IOC_SYS){$(IOC_DEV)}
    ASYN_PREFIX: $(IOC_SYS){$(ASYN_DEV)}
    ENGINEER: "C. Engineer"
    EGU: "urad"
    TWV: "1"
    VELO: "5."
    VBAS: "2.0"
    ACCL: "0.1"
    BDST: "0"
    BVEL: "1"
    BACC: ".2"
    MRES: "0.000001"
    PREC: "3"
    DHLM: "0"
    DLLM: "0"
    INIT: ""
```

## Settings

| Setting                   | Required | Default | Description                                                                                                    |
| ------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------- |
| `type`                    | Yes      | -       | Must be `pi-e621`.                                                                                             |
| `environment.ENGINEER`    | Yes      | -       | Name/contact of the responsible engineer.                                                                      |
| `environment.HOST`        | Yes      | -       | `host:port` of the controller (or terminal server port), passed to `drvAsynIPPortConfigure`.                   |
| `environment.PI_PORT`     | Yes      | -       | asyn port name of the controller created by `E816CreateController`; the low-level IP port is `<PI_PORT>_ASYN`. |
| `environment.SYS`         | Yes      | -       | System prefix of the motor record (`<SYS>{Mono:HDCM-Ax:FP}`) in `asyn_motor.substitutions`.                    |
| `environment.IOC_SYS`     | Yes      | -       | System portion used to build `IOC_PREFIX`/`ASYN_PREFIX`.                                                       |
| `environment.IOC_DEV`     | Yes      | -       | Device portion used to build `IOC_PREFIX`.                                                                     |
| `environment.ASYN_DEV`    | Yes      | -       | Device portion used to build `ASYN_PREFIX`.                                                                    |
| `environment.IOC_PREFIX`  | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                         |
| `environment.ASYN_PREFIX` | Yes      | -       | PV prefix for the `asynComm.db` records.                                                                       |
| `environment.EGU`         | No       | -       | Motor engineering units.                                                                                       |
| `environment.TWV`         | No       | -       | Motor tweak value.                                                                                             |
| `environment.VELO`        | No       | -       | Motor velocity.                                                                                                |
| `environment.VBAS`        | No       | -       | Motor base velocity.                                                                                           |
| `environment.ACCL`        | No       | -       | Motor acceleration time.                                                                                       |
| `environment.BDST`        | No       | -       | Motor backlash distance.                                                                                       |
| `environment.BVEL`        | No       | -       | Motor backlash velocity.                                                                                       |
| `environment.BACC`        | No       | -       | Motor backlash acceleration.                                                                                   |
| `environment.MRES`        | No       | -       | Motor resolution.                                                                                              |
| `environment.PREC`        | No       | -       | Display precision.                                                                                             |
| `environment.DHLM`        | No       | -       | Dial high limit.                                                                                               |
| `environment.DLLM`        | No       | -       | Dial low limit.                                                                                                |
| `environment.INIT`        | No       | -       | Motor record `INIT` string.                                                                                    |

## Notes

- Generates `iocBoot/base.cmd`, which configures the IP port, calls
  `E816CreateController("<PI_PORT>", "<PI_PORT>_ASYN", 1, 50)` and loads
  `asynComm.db`.
- Generates `db/asyn_motor.substitutions` for a single motor
  (`$(PIE621)/db/asyn_motor.db`, alias `vms_pf`) using the motor settings above.
- Inconsistencies: `asyn_motor.substitutions` is not loaded by `base.cmd`, and
  its template references `environment.SYS` and literal `$(environment.<KEY>)`
  macros rather than `ioc.environment` values / plain `$(<KEY>)` macros, so the
  motor settings are not applied as written. The motor record name is also
  hard-coded (`{Mono:HDCM-Ax:FP}`).
