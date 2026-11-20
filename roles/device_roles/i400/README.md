# i400

Deploys a StreamDevice-based IOC for an I400 electrometer, communicating over TCP/IP (e.g. through a terminal server). The IOC is built from [I400-ioc](https://github.com/NSLS2/I400-ioc) (version `0d69784`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
i400-01:
  type: i400
  environment:
    ENGINEER: C. Engineer
    SYS: XF:09IDA-BI
    DEV: "{i400:01}"
    IOC_SYS: XF:09IDA-CT
    IOC_DEV: "{IOC:i400}"
    PORT: E1
    IP: 127.0.0.1
    IP_PORT: 4001
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `i400`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.SYS` | Yes | - | System portion of the device PV prefix (`Sys` macro of `I400.substitutions` and `asyn.db`). |
| `environment.DEV` | Yes | - | Device portion of the device PV prefix (`Dev` macro), e.g. `{i400:01}`. |
| `environment.IOC_SYS` | Yes | - | System portion of the IOC PV prefix; `PREFIX` is set to `$(IOC_SYS)$(IOC_DEV)`. |
| `environment.IOC_DEV` | Yes | - | Device portion of the IOC PV prefix, e.g. `{IOC:i400}`. |
| `environment.PORT` | Yes | - | Name of the asyn IP port created for the device. |
| `environment.IP` | Yes | - | IP address or hostname of the device / terminal server. |
| `environment.IP_PORT` | Yes | - | TCP port on `IP` to connect to (e.g. `4001` for a Moxa terminal server). |

## Notes

- Generates `iocBoot/base.cmd`, which sets `STREAM_PROTOCOL_PATH` to `$(I400)/I400App/src/protocol-files/`, calls `drvAsynIPPortConfigure("$(PORT)", "$(IP):$(IP_PORT)")`, and loads `$(I400)/db/I400.substitutions` and `$(I400)/db/asyn.db` from the module.
- `PREFIX` (used for iocStats/devIocStats records) is set at runtime in `base.cmd` rather than in `environment`, so the common startup does not load the `save_restoreStatus`/`reccaster` records or set the autosave status prefix for this IOC.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- The `dbLoadTemplate(...)` line in `templates/base.cmd.j2` has an extra trailing `)`.
