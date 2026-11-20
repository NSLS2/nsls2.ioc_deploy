# qepro

Deploys an EPICS IOC for Ocean Insight QEPro spectrometers, connected via USB. The IOC is built from [QEPro](https://github.com/NSLS-II/QEPro) (version `734fbdd`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
qepro-01:
  type: qepro

  environment:
    PREFIX: "XF:31ID1-ES{QEPro:Spec-1}"
    PORT: "QEPRO"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `qepro`. |
| `environment.PREFIX` | Yes | - | PV prefix for the `QEPro`, `QEProCollect` and `QEProSpectra` records and the asyn record (`<PREFIX>:ASYNIO`). |
| `environment.PORT` | Yes | `QEPRO` | asyn port name of the driver (`QEProConfig`). |

## Notes

- Installs `/etc/udev/rules.d/90-qepro.rules`, granting the softioc user access (mode `0666`) to USB devices with vendor ID `2457`, then reloads and triggers udev (skipped in containers).
- Generates `iocBoot/base.cmd`, which opens device index `0` and sets the asyn trace mask to `0x9`.
- The common IOC startup (`common.cmd`: iocStats, autosave, reccaster) is not used for this IOC type.
- Building the module clones and compiles the [SeaBreeze](https://github.com/jwlodek/SeaBreeze) library and requires `libusb-devel`.
- The udev rule sets `GROUP` to the softioc user rather than the softioc group.
