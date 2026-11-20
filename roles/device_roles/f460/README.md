# f460

Deploys a StreamDevice-based IOC for an F460 device, communicating over a TCP socket (e.g. via a terminal server). The IOC is built from [F460-ioc](https://github.com/NSLS2/F460-ioc) (version `91a6651`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
f460-01:
  type: f460

  environment:
    ENGINEER: K. Barry
    SYS: XF:31ID-ES
    DEV: "{F460:1}"
    IOC_SYS: XF:31ID-CT
    IOC_DEV: "{IOC:F460}"  # Used for IOC-specific PVs
    PORT: E1
    IP: xf31id1-lab3-tsrv1.nsls2.bnl.local
    IP_PORT: 4008
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `f460`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.SYS` | Yes | - | System portion of the device PV prefix (`Sys` macro of `F460.db` and `asyn.db`). |
| `environment.DEV` | Yes | - | Device portion of the device PV prefix (`Dev` macro of `F460.db` and `asyn.db`). |
| `environment.IOC_SYS` | Yes | - | System portion of the IOC-specific PV prefix; `PREFIX` is set to `$(IOC_SYS)$(IOC_DEV)`. |
| `environment.IOC_DEV` | Yes | - | Device portion of the IOC-specific PV prefix. |
| `environment.PORT` | Yes | - | Name of the asyn IP port. |
| `environment.IP` | Yes | - | IP address or hostname of the device / terminal server. |
| `environment.IP_PORT` | Yes | - | TCP port on `IP` to connect to (e.g. a terminal server serial port). |

## Notes

- Uses the `F460` executable. `STREAM_PROTOCOL_PATH` is set to `${F460}/F460App/src`.
- Loads `F460.db` (with `PINI=YES`, `BUFSZ=12`, `PREC=9`) and `asyn.db` (`ADDR=0`) from the F460 module.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- `PREFIX` is only set at runtime in `base.cmd` (`epicsEnvSet`), not in the Ansible environment. As a result, the common startup loads `iocAdminSoft.db` with `IOC=$(PREFIX)`, but skips `save_restoreStatus.db`, `reccaster.db`, and `save_restoreSet_status_prefix`, which are only added when `PREFIX` (or `IOC_PREFIX`/`CT_PREFIX`) is defined in the environment.
