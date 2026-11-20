# omega_rtc

Deploys a StreamDevice IOC for one or more Omega CNi32 temperature controllers
(RTCs), reached through a terminal server over RS-232 or RS-485. The IOC is
built from [omega_rtc](https://github.com/NSLS-II/omega_rtc_ioc) (version
`a828c22`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
omega_rtc:
  type: "omega_rtc"
  devices:
    - SYS: "XF:31ID1-CT"
      DEV: "{RG:A1-RTC:1}"
      PORT: "tsrv1-p1"
      HOST: "xf31id1-tsrv3.nsls2.bnl.local:4001"
    - SYS: "XF:31ID1-CT"
      DEV: "{RG:A2-RTC:1}"
      PORT: "tsrv1-p2"
      COMM: "RS-232"
      HOST: "xf31id1-tsrv3.nsls2.bnl.local:4002"
    - SYS: "XF:31ID1-CT"
      DEV: "{RG:A3-RTC:1}"
      PORT: "tsrv1-p3"
      COMM: "RS-485"
      HOST: "xf31id1-tsrv3.nsls2.bnl.local:4003"
    - SYS: "XF:31ID1-CT"
      DEV: "{RG:A4-RTC:1}"
      PORT: "tsrv1-p4"
      COMM: "RS-485"
      CHAN: "01"
      HOST: "xf31id1-tsrv3.nsls2.bnl.local:4004"
    - SYS: "XF:31ID1-CT"
      DEV: "{RG:A5-RTC:1}"
      PORT: "tsrv1-p5"
      COMM: "RS-485"
      CHAN: "02"
      HOST: "xf31id1-tsrv3.nsls2.bnl.local:4005"
  environment:
    PREFIX: "XF:31ID1-CT{IOC:RTC}"
    ENGINEER: ""
    SYS: "XF:31ID1-CT"
```

## Settings

| Setting                | Required | Default | Description                                                                                          |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -       | Must be `omega_rtc`.                                                                                 |
| `devices`              | Yes      | -       | List of temperature controllers served by this IOC.                                                  |
| `devices[].SYS`        | Yes      | -       | System portion of the controller's PVs (`Sys` macro).                                                |
| `devices[].DEV`        | Yes      | -       | Device portion of the controller's PVs (`Dev` macro, including braces, e.g. `{RG:A1-RTC:1}`).        |
| `devices[].PORT`       | Yes      | -       | asyn port name for the controller's connection.                                                      |
| `devices[].HOST`       | Yes      | -       | `host:port` of the terminal server port, passed to `drvAsynIPPortConfigure`.                         |
| `devices[].COMM`       | No       | -       | Communication mode, `RS-232` or `RS-485`. If omitted, the device is treated as RS-232.               |
| `devices[].CHAN`       | No       | `01`    | RS-485 address of the controller (`Chan` macro). Only used when `COMM` is `RS-485`; empty otherwise. |
| `environment.PREFIX`   | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                               |
| `environment.ENGINEER` | Yes      | -       | Name/contact of the responsible engineer.                                                            |
| `environment.SYS`      | Yes      | -       | System prefix for the summary alarm PVs (`$(SYS){RG-RTC}Alrm:Sum-Calc`).                             |

## Notes

- Generates `iocBoot/base.cmd`, which sets `STREAM_PROTOCOL_PATH` and, for each
  device, configures an asyn IP port and loads `omegaCNi32_temp.db` and an asyn
  record (`<SYS><DEV>Asyn`).
- Generates `db/alarm.db` with calc records that summarize the `T-I.SEVR` of all
  devices (blocks of up to 12 devices, max 12 blocks) into
  `$(SYS){RG-RTC}Alrm:Sum-Calc` (MINOR at 1, MAJOR at 2).
- Installs a custom `iocBoot/postInit.cmd` that only creates
  `info_settings.req`/`info_positions.req` from DB info and starts their monitor
  sets.
