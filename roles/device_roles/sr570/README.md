# sr570

Deploys a StreamDevice IOC for the Stanford Research Systems SR570 low-noise current preamplifier, communicating over TCP (e.g. via a terminal server). The IOC is built from [NSLS2/BaseStreamDevice](https://github.com/NSLS2/BaseStreamDevice) (version `093e6cf`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
sr570-01:
  type: sr570
  environment:
    DEVICE_IP: "192.168.1.1"
    DEVICE_PORT: 5000
    SYS: "XF:31ID1-ES"
    DEV: "{SR570:1}"
    ENGINEER: "J. Wlodek"
    PORT: "SR570"
  substitutions:
    sr570:
      - filepath: "$(TOP)/db/SR570.template"
        pattern: ["P", "A", "PORT"]
        instances:
          - ["XF:31ID1-ES", "{SR570:1}", "SR570"]
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `sr570`. |
| `environment.DEVICE_IP` | Yes | - | IP address or hostname of the device (or terminal server). |
| `environment.DEVICE_PORT` | Yes | - | TCP port of the device; connected as `DEVICE_IP:DEVICE_PORT`. |
| `environment.SYS` | Yes | - | Base PV prefix; used as the `P` macro for the autosave request file. |
| `environment.DEV` | Yes | - | Device portion of the PV prefix (e.g. `{SR570:1}`); used as the `A` macro for the autosave request file. |
| `environment.PORT` | No | `SR570` | asyn port name created by `drvAsynIPPortConfigure`. |
| `environment.ENGINEER` | No | - | Name/contact info of the responsible engineer, added to the IOC environment. |
| `substitutions.sr570` | No (not in `schema.yml`) | - | Substitutions that load the SR570 records. |
| `substitutions.sr570[].filepath` | - | - | Should be `$(TOP)/db/SR570.template` (installed by this role). |
| `substitutions.sr570[].pattern` | - | - | Macro names: `P`, `A`, `PORT`. |
| `substitutions.sr570[].instances` | - | - | Rows of `[P, A, PORT]` values; should match `SYS`, `DEV`, and `PORT` so the PVs match the autosave request file. |

## Notes

- Installs `db/SR570.template` and the autosave request file `SR570preamp_settings.req` (loaded with `P=$(SYS), A=$(DEV)`); settings are restored from `SR570preamp_settings.sav` in both pass 0 and pass 1.
- The asyn IP port uses `\r\n` input and output terminators.
