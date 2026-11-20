# aduvc

Deploys an areaDetector IOC for USB Video Class (UVC) cameras, such as standard USB webcams. The IOC is built from [ADUVC](https://github.com/areaDetector/ADUVC) (version `86918b6`).

## Example Configuration

Taken from [`examples/cam-usb1/config.yml`](examples/cam-usb1/config.yml):

```yaml
cam-usb1:
  type: aduvc
  environment:
    PREFIX: "XF:31ID1-ES{USB-Cam:1}"
    SERIAL_NUM_OR_PRODUCT_ID: "1234567890"
    ENGINEER: "J. Wlodek"
    XSIZE: 1920
    YSIZE: 1080
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `aduvc`. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`. |
| `environment.ENGINEER` | No | - | Name of the responsible engineer; set as an IOC environment variable. |
| `environment.XSIZE` | Yes | `1920` | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | Yes | `1080` | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.SERIAL_NUM_OR_PRODUCT_ID` | Yes | - | Serial number or product ID used to identify the USB camera (passed to `ADUVCConfig`). |
| `environment.QSIZE` | No | `20` | Queue size for areaDetector plugins. |
| `environment.CBUFFS` | No | `500` | Number of frames in the circular buffer plugin. |
| `environment.MAX_THREADS` | No | `8` | Maximum number of threads per plugin. |
| `environment.PORT` | No | `UVC1` | asyn port name of the camera driver. |
| `environment.FFMSTREAM_PORT` | No | - | HTTP port (>= 8000) for the ffmpeg server. If set, an `ffmstream1:` plugin is loaded and added to autosave. |

## Notes

- Startup sleeps 2 s after `ADUVCConfig` to let the camera initialize.
- An `auto_settings.req` file is generated with `ADUVC_settings.req`, `commonPlugin_settings.req`, and optional ffmpeg/NDCV/NDBar plugin settings.
- Additional environment defaults: `NCHANS=2048`, `NELEMENTS=500000`, `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
