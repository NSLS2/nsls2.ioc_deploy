# es150

Deploys a StreamDevice-based IOC for ES150 DC power supplies, each connected
over TCP (e.g. via a terminal server). The IOC is built from
[es15dcps](https://github.com/NSLS2/es15dcps) (version `80ff267`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
es150-01:
  type: es150
  environment:
    ENGINEER: C. Engineer
    PREFIX: "Egun-Test:"
    SYS: "Egun-Test:"

  devices:
    - HOST: "XX.XX.XX.XX"
      IP_PORT: 4001
      PORT: ES150-1
    - HOST: "XX.XX.XX.XX"
      IP_PORT: 4002
      PORT: ES150-2
    - HOST: "XX.XX.XX.XX"
      IP_PORT: 4003
      PORT: ES150-3

# Schema is in-exact, so caution must be used when copying filepath/pattern
  substitutions:
    dcps: # DC Power Supply
      - filepath: "$(DCPSES150)/db/powersupply.template"
        pattern: ["Sys", "Dev"]
        instances:
          - ["Egun-Test:DC1", "ES150-1"]
          - ["Egun-Test:DC2", "ES150-2"]
          - ["Egun-Test:DC3", "ES150-3"]
```

## Settings

| Setting                          | Required | Default | Description                                                                                                                                                 |
| -------------------------------- | -------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                           | Yes      | -       | Must be `es150`.                                                                                                                                            |
| `environment.ENGINEER`           | Yes      | -       | Name/contact of the responsible engineer.                                                                                                                   |
| `environment.PREFIX`             | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                                                                      |
| `environment.SYS`                | No       | -       | Present in the example but not in the schema and not referenced by the role.                                                                                |
| `devices`                        | Yes      | -       | List (at least one) of power supply connections.                                                                                                            |
| `devices[].HOST`                 | Yes      | -       | IP address or hostname of the power supply / terminal server.                                                                                               |
| `devices[].IP_PORT`              | Yes      | -       | TCP port on `HOST`.                                                                                                                                         |
| `devices[].PORT`                 | Yes      | -       | Name of the asyn IP port created with `drvAsynIPPortConfigure`.                                                                                             |
| `substitutions.dcps`             | Yes      | -       | List of template blocks written to `$(TOP)/db/dcps.substitutions` and loaded with `dbLoadTemplate` in `common.cmd`.                                         |
| `substitutions.dcps[].filepath`  | Yes      | -       | Must be `$(DCPSES150)/db/powersupply.template`.                                                                                                             |
| `substitutions.dcps[].pattern`   | Yes      | -       | Macro names; must be `["Sys", "Dev"]`.                                                                                                                      |
| `substitutions.dcps[].instances` | Yes      | -       | List of `[Sys, Dev]` pairs, one per power supply. In the example, `Sys` is the PV prefix of the supply and `Dev` matches a `devices[].PORT` asyn port name. |

## Notes

- Generates `iocBoot/base.cmd`, which sets `STREAM_PROTOCOL_PATH` to
  `$(DCPSES150)/protocol` and calls
  `drvAsynIPPortConfigure("<PORT>", "<HOST>:<IP_PORT>", 0, 0, 0)` for each entry
  in `devices`.
- As noted in the example, the schema for `substitutions` is inexact, so take
  care when copying `filepath`/`pattern`.
- `environment.SYS` in the example is not used.
