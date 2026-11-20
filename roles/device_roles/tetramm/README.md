# tetramm

Deploys a quadEM-based IOC for the CAEN ELS TetrAMM 4-channel picoammeter (beam position monitor electrometer), communicating over TCP. The IOC is built from [quadEM](https://github.com/epics-modules/quadEM) (version `f5ab1e9`).

## Example Configuration

Taken from [`examples/tetramm-01/config.yml`](examples/tetramm-01/config.yml):

```yaml
tetramm:
  type: "tetramm"
  environment:
    SYS: "XF:09IDC-BI"
    DEV: "{BPM:1}"
    IOC_PREFIX: "$(SYS)$(DEV)"
    ENGINEER: "C. Engineer"
    DEVICE_IP: "127.0.0.1"
    DEVICE_IP_PORT: 10001
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `tetramm`. |
| `environment.SYS` | Yes | - | System part of the PV prefix (`P` macro of the quadEM `TetrAMM.template`). |
| `environment.DEV` | Yes | - | Device part of the PV prefix (`R` macro of the quadEM `TetrAMM.template`). |
| `environment.IOC_PREFIX` | Yes | - | IOC prefix; copied to `PREFIX` and used for the asyn record, plugins, autosave and iocAdmin records. |
| `environment.ENGINEER` | Yes | - | Name of the responsible engineer. |
| `environment.DEVICE_IP` | Yes | - | IP address or hostname of the TetrAMM. |
| `environment.DEVICE_IP_PORT` | Yes | - | TCP port of the TetrAMM (e.g. `10001`). |
| `environment.TEMPLATE` | No | `TetrAMM` | quadEM database template loaded from `$(QUADEM)/db`. |
| `environment.PORT` | No | `TetrAMM` | asyn port name of the TetrAMM driver; the underlying IP port is named `IP_$(PORT)`. |
| `environment.RING_SIZE` | No | `10000` | Ring buffer size passed to `drvTetrAMMConfigure`. |
| `environment.QSIZE` | No | `20` | Queue size for the areaDetector plugins loaded by `commonPlugins.cmd`. |
| `environment.TSPOINTS` | No | `10000` | Number of time-series points for the quadEM time-series plugins. |
| `environment.MAX_THREADS` | No | `8` | Maximum number of plugin threads. |
| `environment.EPICS_CA_MAX_ARRAY_BYTES` | No | `5000000` | Maximum Channel Access array size in bytes. |

## Notes

- `base.cmd` sets `PREFIX` to `$(IOC_PREFIX)`, configures `IP_$(PORT)` with `\r\n` input and `\r` output terminators, loads an asyn record (`$(PREFIX)asyn1`), then loads quadEM's `commonPlugins.cmd` and `saveRestore.cmd`.
- Installs `auto_settings.req` (quadEM settings) into the autosave `req` directory, restored with `P=$(PREFIX)`.
