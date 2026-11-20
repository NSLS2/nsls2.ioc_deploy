# tektronix_afg3k

Deploys a StreamDevice-based IOC for Tektronix AFG3000-series arbitrary function generators, communicating over VXI-11. The IOC is built from [BaseStreamIOC](https://github.com/NSLS2/BaseStreamDevice) (version `093e6cf`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
afg3k:
  type: tektronix_afg3k
  environment:
    P: "XF:31ID1-ES"
    R: "{Tektronix-AFG3K:01}"
    DEVICE_IP: "192.168.1.1"

  substitutions:
    afg3k:
      - filepath: "$(TOP)/db/TektronixAFG3K.template"
        pattern: ["P", "R", "PORT"]
        instances:
          - ["$(P)", "$(R)", "$(PORT)"]
      - filepath: "$(TOP)/db/TektronixAFG3K_Output.template"
        pattern: ["P", "R", "OUTPUT_NUM", "PORT"]
        instances:
          - ["$(P)", "$(R)", "1", "$(PORT)"]
      - filepath: "$(TOP)/db/TektronixAFG3K_Source.template"
        pattern: ["P", "R", "SOURCE_NUM", "PORT"]
        instances:
          - ["$(P)", "$(R)", "1", "$(PORT)"]

    asynRecord:
      - filepath: "$(ASYN)/db/asynRecord.db"
        pattern: ["P", "R", "PORT", "ADDR", "TIMEOUT", "OMAX", "IMAX"]
        instances:
          - ["$(P)", "$(R)AsynIO", "$(PORT)", "0", "1", "0", "0"]
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `tektronix_afg3k`. |
| `environment.P` | Yes | - | PV prefix (system part); combined with `R` to form `PREFIX`. |
| `environment.R` | Yes | - | PV prefix (device part); combined with `P` to form `PREFIX`. |
| `environment.DEVICE_IP` | Yes | - | IP address or hostname of the function generator, passed to `vxi11Configure`. |
| `environment.PORT` | No | `AFG3K` | asyn port name created by `vxi11Configure` in `base.cmd`. |
| `environment.PREFIX` | No | `$(P)$(R)` | IOC PV prefix, used for iocAdmin/autosave status records. |
| `substitutions` | No | - | Map of substitution file name to a list of `filepath`/`pattern`/`instances` entries; each generates `db/<name>.substitutions`, loaded with `dbLoadTemplate`. Available role templates: `TektronixAFG3K.template` (`P`, `R`, `PORT`), `TektronixAFG3K_Output.template` (+ `OUTPUT_NUM`), `TektronixAFG3K_Source.template` (+ `SOURCE_NUM`), `TektronixAFG3K_AM.template` / `TektronixAFG3K_Modulation.template` (+ `SOURCE_NUM`, `MOD_TYPE`), `TektronixAFG3K_PM_FM.template` (+ `SOURCE_NUM`, `MOD_TYPE`, `MOD_NUM`). |

## Notes

- Copies all `TektronixAFG3K*.template` files into `db/` and `afg3k.proto` into `protocol/`.
- `base.cmd` calls `vxi11Configure("$(PORT)", "$(DEVICE_IP)", 0, "0.0", "inst0", 0, 0)` with a `\n` input terminator.
