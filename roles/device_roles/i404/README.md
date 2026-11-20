# i404

Deploys a StreamDevice-based IOC for an I404 electrometer, communicating over TCP/IP (e.g. through a terminal server). The IOC is built from [I404-ioc](https://github.com/NSLS2/I404-ioc) (version `4ea37d0`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
i404-01:
  type: i404
  environment:
    ENGINEER: C. Engineer
    SYS: XF:09IDB-BI
    DEV: "{i404:1}"
    IOC_SYS: XF:09IDB-CT
    IOC_DEV: "{IOC:i404}"
    IP: 127.0.0.1
    IP_PORT: 4001
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `i404`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.SYS` | Yes | - | System portion of the PV prefix for the asyn record (`Sys` macro of `asyn.db`). |
| `environment.DEV` | Yes | - | Device portion of the PV prefix for the asyn record (`Dev` macro), e.g. `{i404:1}`. |
| `environment.IOC_SYS` | Yes | - | System portion of the IOC PV prefix; `PREFIX` is set to `$(IOC_SYS)$(IOC_DEV)`. |
| `environment.IOC_DEV` | Yes | - | Device portion of the IOC PV prefix, e.g. `{IOC:i404}`. |
| `environment.IP` | Yes | - | IP address or hostname of the device / terminal server. |
| `environment.IP_PORT` | Yes | - | TCP port on `IP` to connect to (e.g. `4001` for a Moxa terminal server). |

## Notes

- Generates `iocBoot/base.cmd`, which sets `STREAM_PROTOCOL_PATH` to `$(I404)/i404App/Db`, creates the asyn IP port to `$(IP):$(IP_PORT)`, and loads `$(I404)/db/I404.db` (without macros, so its PV names are fixed by the module) and `$(I404)/db/asyn.db`.
- The asyn port name is always `COM1`, as it is hard coded in the IOC database; there is no `PORT` setting.
- `PREFIX` (used for iocStats/devIocStats records) is set at runtime in `base.cmd` rather than in `environment`, so the common startup does not load the `save_restoreStatus`/`reccaster` records or set the autosave status prefix for this IOC.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
