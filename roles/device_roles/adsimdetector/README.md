# adsimdetector

Deploys an areaDetector simulated detector IOC that generates synthetic images,
useful for testing. The IOC is built from
[ADSimDetector](https://github.com/areaDetector/ADSimDetector) (version
`4b236f4`).

## Example Configuration

Taken from
[`examples/sim-cam-test/config.yml`](examples/sim-cam-test/config.yml):

```yaml
cam-sim1:
  type: "adsimdetector"

  environment:
    PREFIX: "XF:31ID1-ES{Sim-Cam:1}"
    ENGINEER: "J. Wlodek"
    XSIZE: 1024
    YSIZE: 1024
    FFMSTREAM_PORT: 8080
```

## Settings

| Setting                      | Required | Default | Description                                                                                                 |
| ---------------------------- | -------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `type`                       | Yes      | -       | Must be `adsimdetector`.                                                                                    |
| `environment.PREFIX`         | Yes      | -       | Base PV prefix. Detector records are loaded at `$(PREFIX)cam1:`.                                            |
| `environment.ENGINEER`       | No       | -       | Name of the responsible engineer; set as an IOC environment variable.                                       |
| `environment.XSIZE`          | Yes      | `1024`  | Max simulated image width in pixels (passed to `simDetectorConfig`).                                        |
| `environment.YSIZE`          | Yes      | `1024`  | Max simulated image height in pixels (passed to `simDetectorConfig`).                                       |
| `environment.FFMSTREAM_PORT` | No       | -       | HTTP port (>= 8000) for the ffmpeg server. If set, an `ffmstream1:` plugin is loaded and added to autosave. |
| `environment.PORT`           | No       | `SIM1`  | asyn port name of the simDetector driver.                                                                   |
| `environment.QSIZE`          | No       | `20`    | Queue size for areaDetector plugins.                                                                        |
| `environment.CBUFFS`         | No       | `500`   | Number of frames in the circular buffer plugin.                                                             |
| `environment.MAX_THREADS`    | No       | `8`     | Maximum number of threads per plugin.                                                                       |

## Notes

- `PORT`, `QSIZE`, `CBUFFS`, and `MAX_THREADS` are not in `schema.yml` but are
  set by role defaults and can be overridden in `environment`.
- An `auto_settings.req` file is generated with `simDetector_settings.req`,
  `commonPlugin_settings.req`, and optional ffmpeg/NDCV/NDBar plugin settings.
- Additional environment defaults: `NCHANS=2048`,
  `EPICS_DB_INCLUDE_PATH=$(ADCORE)/db`.
