# etherip

Deploys a generic IOC for an Allen-Bradley PLC communicating over EtherNet/IP
via the `ether_ip` driver. The role installs a set of generic PLC database
templates; records are defined by the user via substitutions. The IOC is built
from [ether_ip](https://github.com/epics-modules/ether_ip) (version `b27350b`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
etherip-01:
  type: etherip
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ETHERIP:01}
    PLC_IP: xf31id1-plc1.nsls2.bnl.local
    PLC: "XF31ID1_TST_EPS"
```

## Settings

| Setting                | Required | Default | Description                                                                                                                                                                                                                                                                          |
| ---------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`                 | Yes      | -       | Must be `etherip`.                                                                                                                                                                                                                                                                   |
| `environment.ENGINEER` | Yes      | -       | Name/contact of the responsible engineer.                                                                                                                                                                                                                                            |
| `environment.PREFIX`   | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                                                                                                                                                                                               |
| `environment.PLC_IP`   | Yes      | -       | IP address or hostname of the PLC.                                                                                                                                                                                                                                                   |
| `environment.PLC`      | Yes      | -       | Name of the PLC passed to `drvEtherIP_define_PLC`; referenced by the templates' `PLC` macro (e.g. pass `template_macros: "PLC=$(PLC)"` in substitutions).                                                                                                                            |
| `substitutions`        | No       | -       | Map of substitutions file name to its contents, generating `$(TOP)/db/<name>.substitutions` loaded in `common.cmd` (each with `templates[]` of `filepath`/`pattern`/`instances` and optional `template_macros`). Use to instantiate the installed `$(TOP)/db/plc1-*.template` files. |

## Notes

- Generates `iocBoot/base.cmd`, which sets `EIP_buffer_limit(492)`, initializes
  the EtherIP driver, defines the PLC with
  `drvEtherIP_define_PLC("$(PLC)", "$(PLC_IP)", 0)` (slot 0), and sets
  `EIP_verbosity(6)`.
- Copies these templates into `$(TOP)/db` (records named `$(Sys){$(Dev)}...`):
  - `plc1-ao`, `plc1-bo`: analog/binary outputs (`Sys`, `Dev`, `Sig`, `Tag`,
    `DESC`, `ASG`, ...).
  - `plc1-bi`: binary inputs (`Sys`, `Dev`, `Sig`, `Tag`, `DESC`, `Rate`,
    `ZNAM`, `ONAM`, `ZSV`, `OSV`).
  - `plc1-first`: first-fault indicators (`Sys`, `Dev`, `Sig`, `Seq`, `ArrNum`).
  - `plc1-tc`, `plc1-pt`, `plc1-fm`: thermocouple, pressure transducer, and flow
    meter readings with scaling/alarm macros (`Seq`, `ArrNum`, `ESLO`, `EOFF`,
    `AOFF`, `EGU`, `PREC`, alarm limits).
  - `plc1-va-gv`, `plc1-op-fs`, `plc1-pps-sh`, `plc1-va-rly`: gate valves,
    fluorescent screens, PPS shutters, and vacuum gauge relays.
- The example deploys no substitutions, so no PLC records are loaded beyond the
  standard IOC PVs.
- Several templates use an `ASG` macro, but unlike the `eps` role this role does
  not load an access security file (`asSetFilename`).
- The role creates a `req` directory in the IOC directory, though autosave
  request files are placed under `as/req`.
