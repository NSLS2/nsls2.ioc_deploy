# adprosilica

Deploys an areaDetector IOC for Allied Vision (Prosilica) GigE cameras. The IOC
is built from [ADProsilica](https://github.com/areaDetector/ADProsilica)
(version `9abb772`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
cam-sp1:
  type: "adprosilica"
  environment:
    PREFIX: "XF:31ID1-ES{Sample-Cam:1}"
    ENGINEER: "J. Wlodek"
    XSIZE: 1280
    YSIZE: 720
    CAMERA_ID: "xf31id1-cam1.nsls2.bnl.local" # We don't use the serial number
```

## Settings

| Setting                 | Required | Default | Description                                                                                                         |
| ----------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------- |
| `type`                  | Yes      | -       | Must be `adprosilica`.                                                                                              |
| `environment.ENGINEER`  | Yes      | -       | Name/contact of the responsible engineer.                                                                           |
| `environment.PREFIX`    | Yes      | -       | Base PV prefix. Camera records are loaded at `$(PREFIX)cam1:` and the standard arrays plugin at `$(PREFIX)image1:`. |
| `environment.XSIZE`     | Yes      | -       | Max image width in pixels, used by the areaDetector common plugins.                                                 |
| `environment.YSIZE`     | Yes      | -       | Max image height in pixels, used by the areaDetector common plugins.                                                |
| `environment.CAMERA_ID` | Yes      | -       | IP address or hostname of the camera, passed as the camera ID to `prosilicaConfig` (the serial number is not used). |

## Notes

- `prosilicaConfig("$(PORT)", "$(CAMERA_ID)", 50, 0)` is called with 50 max
  buffers; asyn port `PORT` defaults to `PS1`.
- An `NDStdArrays` plugin (`Image1`, `$(PREFIX)image1:`) is loaded with `Int16`
  data and `NELEMENTS=4177920`, supporting 8, 12, or 16-bit modes.
- Loads the areaDetector common plugins; `auto_settings.req` includes
  `prosilica_settings.req`, `NDStdArrays_settings.req`, and
  `commonPlugin_settings.req`.
- Possible inconsistencies: the role writes `auto_settings.req` to the IOC top
  directory rather than `as/req/` (where autosave looks for it and where other
  AD roles place it), and, unlike other AD roles, it does not set defaults for
  `QSIZE`, `NCHANS`, `CBUFFS`, or `MAX_THREADS`, which the common plugins use.
