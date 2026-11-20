# adandor3

Deploys an areaDetector IOC for Andor cameras supported by the Andor SDK3 (e.g. the Marana used in the example). The IOC is built from [ADAndor3](https://github.com/areaDetector/adandor3) (version `1e33769`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
andor-marana-test:
  type: "adandor3"

  environment:
    ADANDOR3: "/epics/modules/ADAndor3"
    PREFIX: "XF:18IDB-ES{Det:Marana1}"
    PORT: "ANDOR"
    ENGINEER: "C. Engineer"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `adandor3`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PREFIX` | Yes | - | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:`, the image plugin at `$(PREFIX)image1:`. |
| `environment.ADANDOR3` | Yes | - | Path to the ADAndor3 module; used to load `db/andor3.template` and set the autosave request file path. |
| `environment.PORT` | Yes | `ANDOR` | asyn port name of the camera driver (passed to `andor3Config`). |
| `environment.XSIZE` | No | `2048` | Max image width in pixels, used by the areaDetector common plugins. |
| `environment.YSIZE` | No | `2048` | Max image height in pixels, used by the areaDetector common plugins. |
| `environment.HIST_SIZE` | No | `4096` | Histogram size. |
| `environment.QSIZE` | No | `20` | Queue size for areaDetector plugins. |
| `environment.NCHANS` | No | `2048` | Number of channels for time-series plugins. |
| `environment.CBUFFS` | No | `500` | Number of frames in the circular buffer plugin. |
| `environment.NDTYPE` | No | `Int8` | Data type (`TYPE`) of the `image1:` NDStdArrays waveform. |
| `environment.NDFTVL` | No | `UCHAR` | Field type (`FTVL`) of the `image1:` NDStdArrays waveform. |
| `environment.NELMT` | No | `12000000` | Number of elements of the `image1:` NDStdArrays waveform loaded in `base.cmd`. |
| `environment.MAX_THREADS` | No | `8` | Maximum number of threads per plugin. |
| `environment.EPICS_DB_INCLUDE_PATH` | No | `$(ADCORE)/db:$(ADANDOR3)/db` | EPICS database include path. |
| `environment.NELEMENTS` | No | `10000000` | Number of array elements used by the areaDetector common plugins. |

## Notes

- Generates `iocBoot/base.cmd`, which calls `andor3Config("$(PORT)", 0, ...)` (camera index `0`), loads `andor3.template` and configures an `Image1` NDStdArrays plugin, followed by the ADCore `commonPlugins.cmd`.
- An `auto_settings.req` is generated with `andor3_settings.req`, `NDStdArrays_settings.req`, `commonPlugin_settings.req`, and optional ffmpeg (`ffmstream1:`, when `FFMSTREAM_PORT` is set), NDCV (`CV1:`) and NDBar (`Bar1:`) plugin settings.
