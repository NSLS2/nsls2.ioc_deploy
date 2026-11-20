# eguns7

Deploys an IOC for an electron gun controlled by a Siemens S7 PLC, communicating
via the `s7plc` driver over TCP. The IOC is built from
[eguns7](https://github.com/NSLS2/eguns7) (version `4d595bf`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
egun-s7plc-01:
  type: eguns7
  environment:
    ENGINEER: C. Engineer
    PREFIX: "Egun-Test:"
    IP_ADDR: "XX.XX.XX.XX"
    PLC_NAME: "ES"
```

## Settings

| Setting                | Required | Default | Description                                                                           |
| ---------------------- | -------- | ------- | ------------------------------------------------------------------------------------- |
| `type`                 | Yes      | -       | Must be `eguns7`.                                                                     |
| `environment.ENGINEER` | Yes      | -       | Name/contact of the responsible engineer.                                             |
| `environment.PREFIX`   | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                |
| `environment.IP_ADDR`  | Yes      | -       | IP address of the S7 PLC; connected to on port 2000.                                  |
| `environment.PLC_NAME` | Yes      | -       | Name of the PLC connection passed to `s7plcConfigure`, referenced by the PLC records. |

## Notes

- Generates `iocBoot/base.cmd`, which calls
  `s7plcConfigure("$(PLC_NAME)", "$(IP_ADDR)", 2000, 176, 88, 1, 5000, 100)`
  (176-byte input / 88-byte output blocks, big-endian, 5 s receive timeout, 100
  ms send interval) and loads `$(EGUNPLC)/db/es.db`.
- The record prefix for `es.db` is hardcoded to `P=Egun-Test:` in
  `templates/base.cmd.j2` rather than using `$(PREFIX)`, so changing `PREFIX`
  does not change the PLC record names.
