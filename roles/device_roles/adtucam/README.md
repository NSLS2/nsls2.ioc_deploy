# adtucam

Deploys an areaDetector IOC for Tucsen cameras using the TUCAM SDK. Originally written for the AXIS-SXRF-40, which has the Tucsen Dhyana 4040BSI camera electronics. The IOC is built from the [ADTucam driver](https://github.com/NSLS2/ADTucam) (version `c8c1685`).

## Example Configuration

Taken from [`examples/axisDet1/config.yml`](examples/axisDet1/config.yml):

```yaml
axisDet1:
  type: adtucam
  environment:
    ENGINEER: T. Hopkins
    PREFIX: XF:31ID1-ES{AXIS:01}
    PORT: "AXIS1"  # Port name for AD plugin
    QSIZE: 20  # Queue size for the AD plugins
    XSIZE: 4096  # X size of the image
    YSIZE: 4096  # Y size of the image
    NCHANS: 2048 # Maximum number of time
                   # series points in the NDPluginStats plugin
    CBUFFS: 500 # Maximum number of frames buffered in the
                  # NDPluginCircularBuff plugin
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adtucam`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`. |
| `environment.PORT` | Yes | `AXIS1` | asyn port name of the camera driver (passed to `ADTucamConfig`). |
| `environment.QSIZE` | Yes | `20` | Queue size for the areaDetector plugins. |
| `environment.XSIZE` | Yes | `4096` | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | `4096` | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.NCHANS` | Yes | `2048` | Max number of time-series points in the NDPluginStats plugin. |
| `environment.CBUFFS` | Yes | `500` | Max number of frames buffered in the NDPluginCircularBuff plugin. |

## Notes

- The TUCAM SDK and any frame grabber drivers must be installed separately on the host. The example's `verify.yml` skips compilation because the SDK is proprietary.
- `ADTucamConfig` always opens camera index `0`; startup sleeps 3 s after loading the driver.
- In addition to the common plugins, `base.cmd` creates an `NDStdArrays` plugin (`image1:`, `Int32`, `NELEMENTS=5600000`), a second process plugin (`Proc2:`), and a second transform plugin (`Trans2:`, `MAX_THREADS` defaults to 5 as it is not set).
- `EPICS_DB_INCLUDE_PATH` defaults to `$(ADCORE)/db:$(ADTUCAM)/db`.
- Possible inconsistencies: `auto_settings.req` is generated in `as/req/` but not registered in `deploy_ioc_req_file_list`, so it is not used by autosave; it references `NDFileTIFF_settings.req` for `Proc2:TIFF:`, which `base.cmd` does not create. `deploy_ioc_use_common` is `false`, but `common.cmd` is still loaded because `deploy_ioc_use_ad_common` is `true`.
