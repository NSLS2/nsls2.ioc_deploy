# adpicam

Deploys an areaDetector IOC for Princeton Instruments cameras, using the PICam SDK. The IOC is built from [ADPICam](https://github.com/areaDetector/ADPICam.git) (version `0d86fae`).

## Example Configuration

Taken from [`examples/adpicam-01/config.yml`](examples/adpicam-01/config.yml):

```yaml
adpicam-01:
  type: adpicam
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADPICAM:01}
    XSIZE: 2048
    YSIZE: 2048

    NCHANS: 2048
    QSIZE: 2048

    # The maximum number of frames buffered in the NDPluginCircularBuff plugin
    CBUFFS: 8192
    NELEMENTS: 10000000000
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adpicam`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`. |
| `environment.XSIZE` | Yes | `2048` | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | `2048` | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.NCHANS` | Yes | `2048` | Number of channels for time-series plugins. |
| `environment.QSIZE` | Yes | `20` | Queue size for areaDetector plugins. |
| `environment.CBUFFS` | Yes | `500` | Maximum number of frames buffered in the NDPluginCircularBuff plugin. |
| `environment.NELEMENTS` | Yes | - | Number of array elements used by the areaDetector common plugins. |

## Notes

- Requires the PICam SDK installed under `/opt/PrincetonInstruments` and `/opt/pleora`; the role recursively sets both to mode `0755`. The example's `verify.yml` skips module compilation.
- Installs `/etc/udev/rules.d/80-picam.rules`, granting `0666` access to USB devices with vendor `0647` / product `f001`.
- Generates `iocBoot/base.cmd`, which calls `PICamConfig("$(PORT)", 0, 0, 0, 0)` and loads `PICam.template`, followed by the ADCore `commonPlugins.cmd`.
- The autosave directory is named `autosave`; an `auto_settings.req` file is generated with `PICam_settings.req`, `NDStdArrays_settings.req` and `commonPlugin_settings.req`.
- Additional environment defaults: `PORT=PIC1`, `MAX_THREADS=8`; `EPICS_DB_INCLUDE_PATH` is auto-computed from the installed modules.
- Inconsistency: the example's `NELEMENTS: 10000000000` exceeds a 32-bit integer.
