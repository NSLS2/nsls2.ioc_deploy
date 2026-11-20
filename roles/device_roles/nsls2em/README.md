# nsls2em

Deploys an areaDetector-based IOC for the NSLS-II quad electrometer (NSLS2 EM),
with PSC driver (`pscdrv`) records and X/Y EPID feedback loops. The IOC is built
from [nsls2em-ioc](https://github.com/NSLS2/nsls2em-ioc) (version `0e8b996`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
nsls2em-01:
  type: nsls2em
  environment:
    DEVICE_IP: "10.69.58.68"
    SYS: "XF:31ID1-BI"
    DEV: "EM:1"
    DEVICE_SN: "EC0019"
    PREFIX: "$(SYS){$(DEV)}"

    ENGINEER: C. Engineer

  # Settings for PID (if used), PID_PERMIT1 -> A, PID_PERMIT2 -> B
  # ... PID_PERMIT6 -> F
  # PID_PERMITx typically are PV names with logical values
  # FB_ON_CALC specifies logical expression evaluated to enable or disable
  # the PID loop (do not modify the part of expression with J, K and L)
    FB_ON_CALC: "A&&B&&C&&D&&E&&F&&J&&K&&L"
    PID_PERMIT1: "XF:31ID1-OP{A}"  # Those should be PV names
    PID_PERMIT2: "XF:31ID1-OP{B}"
```

## Settings

| Setting                                                 | Required | Default                                                    | Description                                                                                                                                                         |
| ------------------------------------------------------- | -------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                                                  | Yes      | -                                                          | Must be `nsls2em`.                                                                                                                                                  |
| `environment.ENGINEER`                                  | Yes      | -                                                          | Name/contact of the responsible engineer.                                                                                                                           |
| `environment.SYS`                                       | Yes      | -                                                          | System portion of the PV names (`P`/`PriSys`/`Sys` macros).                                                                                                         |
| `environment.DEV`                                       | Yes      | -                                                          | Device portion of the PV names; records use `$(SYS){$(DEV)}`. Also used to name the pscdrv ports (`CmdPort_<DEV>`, `wfm_rx_<DEV>`, `RxPort_<DEV>`).                 |
| `environment.PREFIX`                                    | Yes      | -                                                          | Full device prefix (typically `$(SYS){$(DEV)}`). Used for the asyn record (`asyn1`), startup `dbpf` writes, and the IOC status/autosave/reccaster PVs.              |
| `environment.DEVICE_SN`                                 | Yes      | -                                                          | Device serial number; the calibration file `$(NSLS2EM)/calibration/<DEVICE_SN>.cmd` is loaded after `iocInit`.                                                      |
| `environment.DEVICE_IP`                                 | Yes      | -                                                          | IP address or hostname of the electrometer. Used for the ASCII command port (TCP 17), the pscdrv UDP port (1234), the waveform port (3000) and the status port (7). |
| `environment.PORT`                                      | No       | `NSLS2_EM`                                                 | asyn port name of the `drvNSLS2_VEMConfigure` driver; the low-level IP port is `IP_<PORT>`.                                                                         |
| `environment.QSIZE`                                     | No       | `20`                                                       | Queue size for the areaDetector plugins.                                                                                                                            |
| `environment.RING_SIZE`                                 | No       | `10000`                                                    | Ring buffer size passed to `drvNSLS2_VEMConfigure`.                                                                                                                 |
| `environment.TSPOINTS`                                  | No       | `10000`                                                    | Number of time-series points for the plugins.                                                                                                                       |
| `environment.EPICS_CA_MAX_ARRAY_BYTES`                  | No       | `10000000`                                                 | Maximum CA array size.                                                                                                                                              |
| `environment.FB_ON_CALC`                                | No       | `A&&B&&C&&D&&E&&F&&J&&K&&L`                                | Logical expression that enables/disables the PID loops. Do not modify the `J`, `K` and `L` terms.                                                                   |
| `environment.PID_PERMIT1` ... `environment.PID_PERMIT6` | No       | `1`                                                        | PID permit inputs mapped to `A` ... `F` in `FB_ON_CALC`; typically PV names with logical values.                                                                    |
| `environment.EPICS_DB_INCLUDE_PATH`                     | No       | `$(NSLS2EM)/db:$(PSCDRV)/db:$(ADCORE)/db:$(EPICS_BASE)/db` | EPICS database include path.                                                                                                                                        |

## Notes

- Generates `iocBoot/base.cmd`, which configures the asyn IP port, loads the
  NDArrayBase/quadEM/`nsls2em_RevD` templates, the nsls2em common plugins
  (`$(NSLS2EM)/iocBoot/iocnsls2em/commonPlugins.cmd`), the pscdrv records, and
  two `fb_epid.db` instances (`{$(DEV)}PID_X:` on `Reg49-I`, `{$(DEV)}PID_Y:` on
  `Reg50-I`). The callback queue size is raised to 32768.
- Installs a custom `iocBoot/postInit.cmd` which creates autosave files, loads
  the device calibration file, and applies the startup `dbpf` writes: toggles
  `$(PREFIX)Reg31-Sp` (255 then 0) and sets the `FLNK` of `Reg49-I`/`Reg50-I` to
  the PID input records.
