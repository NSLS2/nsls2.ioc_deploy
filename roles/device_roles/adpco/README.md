# adpco

Deploys an areaDetector IOC for PCO cameras, using the PCO SDK. The IOC is built from [ADPco](https://github.com/paulscherrerinstitute/ADPco) (version `b17fe13`).

## Example Configuration

Taken from [`examples/pco-det1/config.yml`](examples/pco-det1/config.yml):

```yaml
adpco-01:
  type: adpco
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{PCO-Det:1}
    XSIZE: 2560
    YSIZE: 2160
    CAM_ID: 0
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adpco`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`. |
| `environment.XSIZE` | Yes | - | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | - | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.CAM_ID` | No | `0` | Camera ID passed to `ADPcoConfig`. |

## Notes

- Requires the PCO SDK on the host: the module is built against `/opt/pco/pco.sdk`, and the IOC startup exports `LD_LIBRARY_PATH=/opt/pco/pco.sdk/lib:/opt/pco/pco.cpp/lib`. The example's `verify.yml` skips module compilation because of this proprietary SDK.
- Generates `iocBoot/base.cmd`, which calls `ADPcoConfig("$(PORT)", "$(CAM_ID=0)")` and loads `pco.template`, followed by the ADCore `commonPlugins.cmd`.
- The autosave directory is named `autosave`; an `auto_settings.req` file is generated with `pco_settings.req`, `NDStdArrays_settings.req` and `commonPlugin_settings.req`.
- Additional environment defaults: `PORT=PCO1`, `QSIZE=20`, `NCHANS=2048`, `CBUFFS=500`, `MAX_THREADS=8`, `NELEMENTS=5000000`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
