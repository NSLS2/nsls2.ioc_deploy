# cas_switch

Deploys a soft IOC that serves the beamline CA security (CAS) switch PVs from a bundled `cas-switch.db`, with access security configured from the beamline's `cas-switch.acf` file.

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
cas-switch-01:
  type: "cas_switch"
  environment:
    BEAMLINE: "31id1"
    CT_PREFIX: "XF:31ID1-CT"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `cas_switch`. |
| `environment.CT_PREFIX` | Yes | - | PV prefix passed as `CT_PREFIX` to `cas-switch.db`. |
| `environment.BEAMLINE` | Yes | - | Beamline name (e.g. `31id1`); selects the ACF file `/epics/common/bl-cas/bl-cas/<BEAMLINE>/cas-switch.acf`. |

## Notes

- Does not use the standard `st.cmd`. The role generates an `st.cmd` that loads `/epics/common/<hostname>-netsetup.cmd`, loads `cas-switch.db` (copied into the IOC directory from `files/`), calls `asSetFilename(...)`, and runs `iocInit()`.
- No module is required for this role; the `st.cmd` shebang defaults to the system EPICS base `softIoc` (`/usr/lib64/epics/bin/linux-x86_64/softIoc`). This can be overridden with `executable` and `ioc_template_root_path` in the IOC config.
- The ACF file at `/epics/common/bl-cas/bl-cas/<BEAMLINE>/cas-switch.acf` must exist on the host.
