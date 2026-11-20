# advimba

Deploys an areaDetector IOC for Allied Vision cameras (GigE/USB) using the Vimba
SDK and GenICam. The IOC is built from
[ADVimba](https://github.com/areaDetector/ADVimba) (version `34686fe`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
cam-av1:
  type: "advimba"

  environment:
    PREFIX: "XF:31ID1-ES{GigE-Cam:1}"
    ENGINEER: "J. Wlodek"
    CAMERA_ID: "DEV_000F315DFEB9"
    XSIZE: 1024
    YSIZE: 1024
    FFMSTREAM_PORT: 8080
    # GENICAM_DB_FILE: "$(ADGENICAM)/db/AVT_Mako_G030B.template"
```

## Settings

| Setting                       | Required | Default | Description                                                                                                                                                                                            |
| ----------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`                        | Yes      | -       | Must be `advimba`.                                                                                                                                                                                     |
| `environment.PREFIX`          | Yes      | -       | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`.                                                                                                                                         |
| `environment.ENGINEER`        | No       | -       | Name of the responsible engineer; set as an IOC environment variable.                                                                                                                                  |
| `environment.CAMERA_ID`       | Yes      | -       | Camera identifier passed to `ADVimbaConfig`: `DEV_` + uppercase MAC address without colons (e.g. `DEV_000F315DFEB9`), or the camera's IP address (GigE only).                                          |
| `environment.XSIZE`           | Yes      | `1920`  | Max image width in pixels, used by the areaDetector common plugins.                                                                                                                                    |
| `environment.YSIZE`           | Yes      | `1080`  | Max image height in pixels, used by the areaDetector common plugins.                                                                                                                                   |
| `environment.FFMSTREAM_PORT`  | No       | -       | HTTP port (>= 8000) for the ffmpeg server. If set, an `ffmstream1:` plugin is loaded and added to autosave.                                                                                            |
| `environment.QSIZE`           | No       | `20`    | Queue size for areaDetector plugins.                                                                                                                                                                   |
| `environment.CBUFFS`          | No       | `500`   | Number of frames in the circular buffer plugin.                                                                                                                                                        |
| `environment.MAX_THREADS`     | No       | `8`     | Maximum number of threads per plugin.                                                                                                                                                                  |
| `environment.PORT`            | No       | `VMB1`  | asyn port name of the camera driver.                                                                                                                                                                   |
| `environment.GENICAM_DB_FILE` | -        | -       | Not in `schema.yml`, but `base.cmd` always loads `$(GENICAM_DB_FILE)` as the camera-model-specific GenICam features database (e.g. `$(ADGENICAM)/db/AVT_Mako_G030B.template`), so it must be provided. |

## Notes

- Depends on the ADGenICam module. Defaults set
  `GENICAM_GENTL64_PATH=$(ADVIMBA)/bin/linux-x86_64` and
  `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db:$(ADGENICAM)/db`.
- Startup sleeps 3 s before `ADVimbaConfig` so the IOC reliably reconnects to
  the camera after a restart.
- An `auto_settings.req` file is generated with `vimba_settings.req`,
  `commonPlugin_settings.req`, and optional ffmpeg/NDCV/NDBar plugin settings.
- Additional environment defaults: `NCHANS=2048`, `NELEMENTS=500000`.
