# adkinetix

Deploys an areaDetector IOC for a Kinetix camera, using the PVCAM SDK. The IOC
is built from [adkinetix](https://github.com/NSLS2/ADKinetix) (version
`aa87406`).

## Example Configuration

Taken from
[`examples/kinetix-det1/config.yml`](examples/kinetix-det1/config.yml):

```yaml
kinetix-det1:
  type: adkinetix
  environment:
    PREFIX: "XF:31ID1-ES{Kinetix-Det:1}"
    PORT: "KTX"
    XSIZE: 3200
    YSIZE: 3200
```

## Settings

| Setting                      | Required | Default | Description                                                                                                 |
| ---------------------------- | -------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `type`                       | Yes      | -       | Must be `adkinetix`.                                                                                        |
| `environment.PREFIX`         | Yes      | -       | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`.                                              |
| `environment.XSIZE`          | Yes      | `3200`  | Max image width in pixels, used by the areaDetector common plugins.                                         |
| `environment.YSIZE`          | Yes      | `3200`  | Max image height in pixels, used by the areaDetector common plugins.                                        |
| `environment.FFMSTREAM_PORT` | No       | -       | HTTP port (>= 8000) for the ffmpeg server. If set, an `ffmstream1:` plugin is loaded and added to autosave. |
| `environment.QSIZE`          | No       | `20`    | Queue size for areaDetector plugins.                                                                        |
| `environment.CBUFFS`         | No       | `500`   | Number of frames in the circular buffer plugin.                                                             |
| `environment.MAX_THREADS`    | No       | `8`     | Maximum number of threads per plugin.                                                                       |
| `environment.PORT`           | No       | `KTX`   | asyn port name of the camera driver (passed to `ADKinetixConfig`).                                          |

## Notes

- Requires the PVCAM SDK installed under `/opt/pvcam` on the host. Since the
  softioc account does not load `profile.d`, the IOC startup exports
  `PVCAM_VERSION` (read from `/opt/pvcam/pvcam.version`),
  `PVCAM_UMD_PATH=/opt/pvcam/drivers/user-mode`, and
  `PVCAM_SDK_PATH=/opt/pvcam/sdk`.
- `ADKinetixConfig` always opens camera index `0`; startup sleeps 2 s to let the
  camera initialize.
- The autosave directory is named `autosave`; an `auto_settings.req` file is
  generated with `ADKinetix_settings.req`, `commonPlugin_settings.req`, and
  optional ffmpeg/NDCV/NDBar plugin settings.
- Additional environment defaults: `NCHANS=2048`, `NELEMENTS=5000000`,
  `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
