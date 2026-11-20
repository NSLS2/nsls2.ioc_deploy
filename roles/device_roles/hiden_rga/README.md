# hiden_rga

Deploys a StreamDevice-based IOC for a Hiden Analytical residual gas analyzer (RGA), communicating over TCP. The IOC is built from [HidenRGA-ioc](https://github.com/NSLS2/HidenRGA-ioc) (version `0744058`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
hiden_rga-01:
  type: hiden_rga
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-VA{HIDEN_RGA:01}
    PORT: "RGA1"
    HOST: "127.0.0.1"
    IP_PORT: 5025
    Sys: "XF:31ID1-VA"
    Dev: "{HIDEN_RGA:01}"
    CntlSys: "XF:31ID1-CT"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `hiden_rga`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). |
| `environment.PORT` | Yes | - | Name of the asyn IP port. |
| `environment.HOST` | Yes | - | IP address or hostname of the RGA. |
| `environment.IP_PORT` | Yes | - | TCP port on `HOST` to connect to. |
| `environment.Sys` | Yes | - | System portion of the device PV prefix (`Sys` macro of the RGA templates). |
| `environment.Dev` | Yes | - | Device portion of the device PV prefix (`Dev` macro of the RGA templates). |
| `environment.CntlSys` | Yes | - | Control system prefix. Required by the schema but not referenced by this role's startup template. |

## Notes

- Uses the `HidenRGA` executable. `STREAM_PROTOCOL_PATH` is set to `$(HIDEN_RGA)/protocol`.
- Loads `hiden_rga_global`, `hiden_rga_bar`, `hiden_rga_prfl`, `hiden_rga_mid`, and `hiden_rga_degas` templates from the module, all with `Sys`, `Dev`, and `PORT` macros.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- `base.cmd` loads `$(HIDEN_RGA)/db/reccaster.db` with `P=$(PREFIX)RecSync`, and the common startup also loads `$(EPICS_BASE)/db/reccaster.db` with the same prefix because `PREFIX` is set. This may result in duplicate record definitions.
