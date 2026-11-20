# va

Deploys a vacuum (VA) IOC that talks to vacuum gauge controllers (MKS 937B) and
ion pump controllers (Gamma MPCq, Agilent 4UHV, Varian) over TCP (e.g. via
terminal servers) using StreamDevice. The IOC is built from
[va-ioc](https://github.com/nsls2/va-ioc) (version `84e0991`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
va-01:
  type: va

  # SYS and DEV: used to generate prefix for each device
  # IOC_SYS and IOC_DEV: used to generate prefix for IOC-specific PVs
  # HOST may be an IP address or host name, IP_PORT is the host port number
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{VA:01}

  devices:
    - HOST: "10.66.66.71"
      IP_PORT: 4001
      PORT: tsrv1-P1
    - HOST: "10.66.66.71"
      IP_PORT: 4002
      PORT: tsrv1-P2
    - HOST: "10.66.66.71"
      IP_PORT: 4003
      PORT: tsrv1-P3
    - HOST: "10.66.66.71"
      IP_PORT: 4004
      PORT: tsrv1-P4
    - HOST: "10.66.66.80"
      IP_PORT: 4001
      PORT: tsrv10-P1
    - HOST: "10.66.66.80"
      IP_PORT: 4002
      PORT: tsrv10-P2
    - HOST: "10.66.66.80"
      IP_PORT: 4003
      PORT: tsrv10-P3
    - HOST: "10.66.66.82"
      IP_PORT: 4001
      PORT: tsrv12-P1
    - HOST: "10.66.66.82"
      IP_PORT: 4002
      PORT: tsrv12-P2

    - HOST: "10.66.66.141"
      IP_PORT: 23
      PORT: xf09id1-ipc1
    - HOST: "10.66.66.142"
      IP_PORT: 23
      PORT: xf09id1-ipc2
    - HOST: "10.66.66.143"
      IP_PORT: 23
      PORT: xf09id1-ipc3
    - HOST: "10.66.66.144"
      IP_PORT: 23
      PORT: xf09id1-ipc4

# Schema is in-exact, so caution must be used when copying filepath/pattern
  substitutions:
    vgc: # Vacuum Gauge Controller
    # Vacuum Gauge Controller
      - filepath: "$(VA)/db/mks937b_controller.template"
        pattern: ["Sys", "Cntl", "PORT", "ADR"]
        instances:
          - ["XF:09IDA-VA", "{VGC:1}", "tsrv1-P1", "253"]

    # Cold Cathode Gauge and relay
      - filepath: "$(VA)/db/mks937b_ccg.template"
        pattern: ["Sys", "Dev", "CHAN", "PORT", "ADR", "Cntl"]
        instances:
          - ["XF:09IDA-VA", "{Msk:WB-CCG:1}", "1", "tsrv1-P1", "253", "{VGC:1}"]

      - filepath: "$(VA)/db/mks937b_relay_ccg.template"
        pattern:
          - "Sys"
          - "Dev"
          - "SPNUM"
          - "PORT"
          - "ADR"
          - "Cntl"
        instances:
          - [
            "XF:09IDA-VA",
            "{Msk:WB-CCG:1}",
            "1",
            "tsrv1-P1",
            "253",
            "{VGC:1}"
          ]

    # Thermocouple Gauge and relay
      - filepath: "$(VA)/db/mks937b_pirg.template"
        pattern:
          - "Sys"
          - "Dev"
          - "CHAN"
          - "PORT"
          - "ADR"
          - "Cntl"
          - "SPNUM1"
          - "SPNUM2"
        instances:
          - [
            "XF:09IDA-VA",
            "{Msk:WB-TCG:1}",
            "5",
            "tsrv1-P1",
            "253",
            "{VGC:1}",
            "9",
            "10"
          ]

      - filepath: "$(VA)/db/mks937b_relay_pirg.template"
        pattern: ["Sys", "Dev", "SPNUM", "PORT", "ADR", "Cntl"]
        instances:
          - ["XF:09IDA-VA", "{Msk:WB-TCG:1}", "9", "tsrv1-P1", "253", "{VGC:1}"]

    ipc: # Ion Pump Controller, Pump, and Pump Relay
      - filepath: "$(VA)/db/gammampcq_controller.template"
        pattern: ["Sys", "Cntl", "PORT"]
        instances:
          - ["XF:09IDA-VA", "{IPC:1}", "xf09id1-ipc1"]

      - filepath: "$(VA)/db/gammampcq_ip.template"
        pattern: ["Sys", "Dev", "CHAN", "PORT", "Cntl"]
        instances:
          - ["XF:09IDA-VA", "{Msk:WB-IP:1}", "1", "xf09id1-ipc1", "{IPC:1}"]

      - filepath: "$(VA)/db/gammampcq_setpoint.template"
        pattern: ["Sys", "Dev", "CHAN", "SPNUM", "PORT", "Cntl"]
        instances:
          - [
            "XF:09IDA-VA",
            "{Msk:WB-IP:1}",
            "1",
            "1",
            "xf09id1-ipc1",
            "{IPC:1}"
          ]

    asyn: # Asyn Port configurations
      - filepath: "$(EPICS_BASE)/db/asynRecord.db"
        pattern: ["P", "R", "PORT", "ADDR", "IMAX", "OMAX"]
        instances:
          - ["XF:09IDA-CT", "{VGC:1}Asyn", "tsrv1-P1", "0", "256", "256"]
```

## Settings

| Setting                            | Required | Default | Description                                                                                                                                                                                                              |
| ---------------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`                             | Yes      | -       | Must be `va`.                                                                                                                                                                                                            |
| `environment.ENGINEER`             | Yes      | -       | Name/contact of the responsible engineer.                                                                                                                                                                                |
| `environment.PREFIX`               | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                                                                                                                                   |
| `devices`                          | Yes      | -       | List (at least one) of TCP connections to create.                                                                                                                                                                        |
| `devices[].HOST`                   | Yes      | -       | IP address or hostname of the device / terminal server.                                                                                                                                                                  |
| `devices[].IP_PORT`                | Yes      | -       | TCP port on `HOST`.                                                                                                                                                                                                      |
| `devices[].PORT`                   | Yes      | -       | asyn port name created by `drvAsynIPPortConfigure("<PORT>", "<HOST>:<IP_PORT>")`; referenced by the `PORT` macro in substitutions.                                                                                       |
| `substitutions.vgc`                | Yes      | -       | List of vacuum gauge controller database blocks, written to `db/vgc.substitutions`. `filepath` must be one of `$(VA)/db/mks937b_{controller,ccg,relay_ccg,pirg,relay_pirg}.template`.                                    |
| `substitutions.ipc`                | Yes      | -       | List of ion pump controller database blocks, written to `db/ipc.substitutions`. `filepath` must be one of the `$(VA)/db/gammampcq_*`, `agilent4uhv*`, `varian*` or `cell-tsp-download` templates listed in `schema.yml`. |
| `substitutions.asyn`               | Yes      | -       | List of asyn record blocks, written to `db/asyn.substitutions`. `filepath` must be `$(EPICS_BASE)/db/asynRecord.db`.                                                                                                     |
| `substitutions.<name>[].filepath`  | Yes      | -       | Database template to load.                                                                                                                                                                                               |
| `substitutions.<name>[].pattern`   | Yes      | -       | List of macro names for the template (allowed names restricted per block in `schema.yml`, e.g. `Sys`, `Dev`, `Cntl`, `PORT`, `ADR`, `CHAN`, `SPNUM`; `P`, `R`, `PORT`, `ADDR`, `IMAX`, `OMAX` for `asyn`).               |
| `substitutions.<name>[].instances` | Yes      | -       | List of rows of macro values, one per instance, in the same order as `pattern` (4-8 values for `vgc`, 1-8 for `ipc`, exactly 6 for `asyn`).                                                                              |

## Notes

- Generates `iocBoot/base.cmd`, which sets `STREAM_PROTOCOL_PATH=$(VA)/protocol`
  and creates one `drvAsynIPPortConfigure` port per entry in `devices`. Each
  `substitutions` key becomes `db/<key>.substitutions`, loaded with
  `dbLoadTemplate` by the common startup.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- The schema is inexact: it only checks that each `filepath`/`pattern` value is
  from an allowed list, not that the pattern matches the chosen template, so
  take care when copying blocks.
- The comment in `example.yml` mentions `SYS`, `DEV`, `IOC_SYS` and `IOC_DEV`
  environment variables, which are not used by this role or its schema.
