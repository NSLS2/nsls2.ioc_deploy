# zubpm

Deploys an IOC for a zuBPM beam position monitor, communicating with the BPM
over TCP (port 3000) using pscdrv. The IOC is built from
[zubpm-ioc](https://github.com/NSLS2/zubpm-ioc.git) (version `cedd09e`), with
[pscdrv](https://github.com/mdavidsaver/pscdrv) as a dependency.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
zubpm-c28-test:
  type: zubpm
  environment:
    ENGINEER: "Y. Hu"
    IOCNAME: "C28test"
    "NO": 2
    PSC: "psc2"
    ZBPM_IP: "10.0.142.100"
    PX: "C28test{BPM:2}"
    ALIVELEN: 8000
    TLIVELEN: 8000
    ALEN: 500000
    TLEN: 500000
    FLEN: 500000
```

## Settings

| Setting                | Required | Default | Description                                                                                                                |
| ---------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -       | Must be `zubpm`.                                                                                                           |
| `environment.ENGINEER` | Yes      | -       | Name/contact of the responsible engineer.                                                                                  |
| `environment.IOCNAME`  | Yes      | -       | PV prefix base (`P` macro of all databases). Overrides the default `IOCNAME` environment variable (the IOC instance name). |
| `environment.NO`       | Yes      | -       | BPM number (`NO`/`B` macro). Quote the key (`"NO"`) so YAML does not parse it as a boolean.                                |
| `environment.PSC`      | Yes      | -       | Name of the PSC connection created by `createPSC`.                                                                         |
| `environment.ZBPM_IP`  | Yes      | -       | IP address or hostname of the BPM; connected to on port 3000.                                                              |
| `environment.PX`       | Yes      | -       | Not referenced by the role's templates.                                                                                    |
| `environment.ALIVELEN` | Yes      | -       | ADC live waveform length (`ADC_LIVE_WFM_LEN`).                                                                             |
| `environment.TLIVELEN` | Yes      | -       | Turn-by-turn live waveform length (`TBT_LIVE_WFM_LEN`).                                                                    |
| `environment.ALEN`     | Yes      | -       | ADC waveform length (`ADC_WFM_LEN`, `ADC_LEN`).                                                                            |
| `environment.TLEN`     | Yes      | -       | Turn-by-turn waveform length (`TBT_WFM_LEN`, `TBT_LEN`).                                                                   |
| `environment.FLEN`     | Yes      | -       | Fast acquisition waveform length (`FA_LEN`).                                                                               |

## Notes

- `base.cmd` temporarily sets `TOP` to the module directory to load `zubpm.db`,
  `FA.db`, `TBT.db`, `ADC.db`, 6x `SFP.db`, `SA.db`, `Power.db`, `Temp.db` and
  `FFT.db` from its `db/` directory, then restores `TOP` to the IOC directory.
  The IOC executable is `zbpm`; the module requires the `fftw-devel` package.
- `deploy_ioc_use_common` is `false`, so the common startup (iocStats, autosave,
  reccaster) is not loaded and no `PREFIX` is needed.
- `PX` is required by the schema but unused by the role.
