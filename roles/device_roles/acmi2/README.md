# acmi2

Deploys the ACMI-2 (Accelerator Charge Monitor Interlock) IOC used at NSLS-II. The IOC monitors injected beam charge from the electron gun and enforces Accelerator Safety Envelope (ASE) limits by disabling the gun on violation, communicating with the hardware through a PSC (Portable Streaming Controller). The IOC is built from [acmi2-ioc](https://github.com/NSLS2/acmi2-ioc) (version `e503d9f`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
acmi2-ioc1:
  type: acmi2
  environment:
    ENGINEER: Y. Hu
    IOCNAME: lab
    UNIT: A
    PSC_IP: "10.0.142.128"
    PSC_PORT: 3000
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `acmi2`. |
| `environment.IOCNAME` | Yes | IOC instance name | PV prefix macro, passed as `P` to every `dbLoadRecords` call. Overrides the default `IOCNAME` (the IOC instance name). |
| `environment.UNIT` | Yes | - | Unit macro, passed as `NO` to every `dbLoadRecords` call. |
| `environment.PSC_IP` | Yes | - | IP address or hostname of the PSC device (passed to `createPSC`). |
| `environment.PSC_PORT` | No | `3000` | TCP port of the PSC device (1-65535). |
| `environment.ENGINEER` | No | - | Name/contact of the responsible engineer; exported via `epicsEnvSet`. |

## Notes

- Depends on the PSC driver [`pscdrv`](https://github.com/mdavidsaver/pscdrv), which is automatically built as a module dependency before `acmi2-ioc` is compiled (`fftw-devel` is also installed).
- Generates `iocBoot/base.cmd`, which loads `ADC.db`, `TP.db` (for `T=1..3`), `Beam.db`, `Tail2.db`, `lstats.db`, `control.db`, `pulse_stats.db`, `eeprom.db` and `adc_data.db`, sets `PSCDebug=1`, and creates PSC port `PSCA` with a 70000-byte send block size.
- The standard `common.cmd` is disabled (`deploy_ioc_use_common: false`), so iocStats, reccaster and autosave are not configured by this role.
- Copies the `Correction`, `COW`, `gui`, `opi`, `PM`, `python` and `settings` directories from the module source into the IOC directory; `Correction`, `COW` and `settings` are made world-writable (`02777`).
