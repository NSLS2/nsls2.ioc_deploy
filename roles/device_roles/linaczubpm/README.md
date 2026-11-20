# linaczubpm

Deploys an IOC for a linac zuBPM beam position monitor, communicating with the BPM electronics via the PSC driver (`pscdrv`). The IOC is built from [zubpm-ioc](https://github.com/NSLS2/zubpm-ioc) (version `aca9b87`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
linaczubpm-01:
  type: linaczubpm
  environment:
    ENGINEER: C. Engineer
    PREFIX: "LN-BI{BPM:1}"
    BPMNo: BPM1
    BPMIP: ""
    ALIVELEN: ""
    FLEN: ""
    TLEN: ""
    ALEN: ""
    PSCNo: ""
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `linaczubpm`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | PV prefix (`P` macro) for all BPM databases, and for the IOC admin/autosave records. |
| `environment.BPMNo` | Yes | - | BPM identifier, passed as the `NO` (or `B` for `SFP.db`) macro. |
| `environment.BPMIP` | Yes | - | IP address of the BPM, passed (unquoted) to `createPSC`. |
| `environment.ALIVELEN` | Yes | - | Length of the live ADC waveform (`ADC_LIVE_WFM_LEN`). |
| `environment.FLEN` | Yes | - | Fast-acquisition (FA) waveform length (`FA_LEN`). |
| `environment.TLEN` | Yes | - | Turn-by-turn waveform length (`TBT_WFM_LEN` / `TBT_LEN`). |
| `environment.ALEN` | Yes | - | ADC waveform length (`ADC_WFM_LEN` / `ADC_LEN`). |
| `environment.PSCNo` | Yes | - | Name of the PSC instance passed to `createPSC`. |

## Notes

- Generates `iocBoot/base.cmd`, which loads `zubpm.db`, `FA.db`, `TBT.db`, `ADC.db`, six `SFP.db` instances (`S=0..5`), `SA.db`, `Power.db`, `Temp.db`, `FFT.db` and `lstats.db` from `$(LINZUBPM)/db`, then sets `PSCDebug` to 1 and calls `createPSC("$(PSCNo)", $(BPMIP), 3000, 0)` (TCP port 3000).
- The module depends on `pscdrv` and requires the `fftw-devel` package to build.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- Possible issues:
  - The example leaves `BPMIP`, `PSCNo` and the waveform lengths empty; real values must be supplied.
  - The `zubpm.db` line in `templates/base.cmd.j2` is truncated (ends with `,$` and no closing quote/parenthesis).
  - That line also references `$(TLIVELEN)` (`TBT_LIVE_WFM_LEN`), which is not in the schema or example.
