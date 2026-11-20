# mrftiming

Deploys an IOC for a Micro-Research Finland (MRF) event receiver (EVR),
communicating with the device over UDP/IP. The IOC is built from
[MRFTiming](https://github.com/NSLS2/MRFTiming) (version `3bb9fcf`).

## Example Configuration

Taken from
[`examples/mrftiming-01/config.yml`](examples/mrftiming-01/config.yml):

```yaml
mrftiming-01:
  type: mrftiming
  environment:
    IP: "10.70.11.26"
    P: "C29-TST"
```

## Settings

| Setting                | Required | Default | Description                                                                                                                       |
| ---------------------- | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -       | Must be `mrftiming`.                                                                                                              |
| `environment.IP`       | Yes      | -       | IP address or hostname of the EVR; passed to `mrfUdpIpEvrDevice("EVR01", ...)`.                                                   |
| `environment.P`        | Yes      | -       | Base PV prefix (`P` macro) for the EVR records (`vme-evr-230rf.db`, autosave menu, write-all-settings, and `misc.substitutions`). |
| `environment.ENGINEER` | No       | -       | Name/contact of the responsible engineer.                                                                                         |

## Notes

- Generates `iocBoot/base.cmd`, which creates EVR device `EVR01` and loads
  `vme-evr-230rf.db`, `mrf-autosave-menu.db` (presets under `Presets:`, config
  name `evr01_preset`), `mrf-write-all-settings-with-status.db` and
  `$(MRFTiming)/db/misc.substitutions`.
- Copies `files/auto_settings.req` (which includes `vme-evr-230rf.req`) to
  `as/req/auto_settings.req`; it is monitored with macros `P=$(PREFIX), R=""`.
  Autosave files are also generated from DB info (`makeAutosaveFiles`).
- The example's `verify.yml` sets `skip_compilation: true`.
- Inconsistencies: `PREFIX` is not in the schema or example, but is used by the
  autosave request macros and by the common `iocAdminSoft.db` load. `base.cmd`
  also references the `R`, `UO_*` and `TB_*` macros, which the role does not
  set.
