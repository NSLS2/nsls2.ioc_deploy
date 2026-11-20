# mdrive

Deploys a motor IOC for Schneider Electric / IMS MDrive Plus integrated stepper
motors, each connected over TCP/IP (e.g. via a terminal server port). The IOC is
built from [mdrive-ioc](https://github.com/NSLS2/mdrive-ioc) (version
`8bc9a09`).

## Example Configuration

Taken from [`examples/mdrive-g1/config.yml`](examples/mdrive-g1/config.yml):

```yaml
mdrive-g1:
  type: mdrive
  environment:
    ENGINEER: C. Engineer
    PREFIX: "XF:31ID1-CT{IOC:MDrvG1}"
    SYS_IOC: "XF:31ID1-CT"
    IP_PORT: 503
    SYS: "XF:31ID1-OP"
    MRES: 4.9609375e-5
    VBAS: 1.0
    VELO: 2
    VMAX: 5
    ACCL: 0.2
    EGU: "mm"
  devices:
    - host: "127.0.0.1"
      io_port: P1
      Sys: "XF:31ID1-OP"
      Dev: "MDrive:1"
      CntlDev: "A-MDrv:1"
      DESC: "MDrive 1"
      ALIAS: "mdrive1"
    - host: "127.0.0.1"
      io_port: P2
      Dev: "MDrive:2"
      DESC: "MDrive 2"
      ALIAS: "mdrive2"
    - host: "127.0.0.1"
      io_port: P3
      Dev: "MDrive:3"
      DESC: "MDrive 3"
      ALIAS: "mdrive3"
    - host: "127.0.0.1"
      io_port: P4
      Dev: "MDrive:4"
      DESC: "MDrive 4"
      ALIAS: "mdrive4"
    - host: "127.0.0.1"
      io_port: P5
      Sys: "XF:31ID1-OP"
      Sys_IOC: "XF:31ID1-CT:1"
      Dev: "MDrive:5"
      MRES: 9.765625e-6
      EGU: "um"
      DESC: "MDrive 5"
      ALIAS: "mdrive5"
    - host: "127.0.0.1"
      io_port: P6
      Dev: "MDrive:6"
      DESC: "MDrive 6"
      ALIAS: "mdrive6"
```

## Settings

| Setting                | Required | Default               | Description                                                                                               |
| ---------------------- | -------- | --------------------- | --------------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -                     | Must be `mdrive`.                                                                                         |
| `environment.ENGINEER` | Yes      | -                     | Name/contact of the responsible engineer.                                                                 |
| `environment.PREFIX`   | Yes      | -                     | IOC prefix for iocAdmin, autosave status and reccaster records.                                           |
| `environment.SYS_IOC`  | Yes      | -                     | Default system prefix for the per-device asyn records (`<SYS_IOC>{<CntlDev or Dev>}Asyn`).                |
| `environment.IP_PORT`  | Yes      | -                     | TCP port used for every device connection (`<host>:<IP_PORT>`).                                           |
| `environment.SYS`      | Yes      | -                     | Default system prefix for motor PVs (`<SYS>{<Dev>}Mtr`).                                                  |
| `environment.MRES`     | Yes      | -                     | Default motor resolution (`MRES`).                                                                        |
| `environment.VBAS`     | No       | -                     | Default base velocity (`VBAS`).                                                                           |
| `environment.VELO`     | No       | -                     | Default velocity (`VELO`).                                                                                |
| `environment.VMAX`     | No       | -                     | Default maximum velocity (`VMAX`).                                                                        |
| `environment.ACCL`     | No       | -                     | Default acceleration time (`ACCL`).                                                                       |
| `environment.EGU`      | Yes      | -                     | Default engineering units (`EGU`).                                                                        |
| `devices`              | Yes      | -                     | List (at least one) of MDrive motors; each gets its own asyn IP port and `ImsMDrivePlusCreateController`. |
| `devices[].host`       | Yes      | -                     | IP address or hostname to connect to.                                                                     |
| `devices[].io_port`    | Yes      | -                     | asyn IP port name, matching `^P\d+$` (e.g. `P1`); the motor controller port is `<io_port>_Mtr`.           |
| `devices[].Sys`        | No       | `environment.SYS`     | System prefix for this motor's PVs.                                                                       |
| `devices[].Sys_IOC`    | No       | `environment.SYS_IOC` | System prefix for this device's asyn record.                                                              |
| `devices[].Dev`        | Yes      | -                     | Device name; motor PV is `<Sys>{<Dev>}Mtr`, extra IMS records use `<Sys>{<Dev>}`.                         |
| `devices[].CntlDev`    | No       | `Dev`                 | Device name used for the asyn record (`<Sys_IOC>{<CntlDev>}Asyn`).                                        |
| `devices[].MRES`       | No       | `environment.MRES`    | Per-motor resolution override.                                                                            |
| `devices[].VBAS`       | No       | `environment.VBAS`    | Per-motor base velocity override.                                                                         |
| `devices[].VELO`       | No       | `environment.VELO`    | Per-motor velocity override.                                                                              |
| `devices[].VMAX`       | No       | `environment.VMAX`    | Per-motor maximum velocity override.                                                                      |
| `devices[].ACCL`       | No       | `environment.ACCL`    | Per-motor acceleration override.                                                                          |
| `devices[].EGU`        | No       | `environment.EGU`     | Per-motor engineering units override.                                                                     |
| `devices[].DESC`       | Yes      | -                     | Motor record description.                                                                                 |
| `devices[].ALIAS`      | No       | `<Dev>Mtr`            | Alias for the motor record.                                                                               |

## Notes

- Generates `iocBoot/base.cmd`, `db/motor.substitutions`
  (`$(MDRIVE)/db/motor.db` and `$(IMS)/db/IMS_extra.db` per device) and
  `db/asynRecord.substitutions` (one `asynRecord.db` per device).
- The module depends on the `ims` motor module.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- `VBAS`, `VELO`, `VMAX` and `ACCL` are optional in the schema but have no
  fallback in `templates/motor.substitutions.j2`; if neither the device nor
  `environment` sets them, rendering will likely fail.
