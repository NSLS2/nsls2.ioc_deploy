# adscanpb

Deploys an ADScanPB areaDetector IOC, which plays back past scan data (from
local files or from Tiled) as detector frames, triggered by an external PV. The
IOC is built from [ADScanPB](https://github.com/NSLS2/ADScanPB.git) (version
`f54e2c1`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adscanpb-01:
  type: adscanpb
  environment:
    ENGINEER: C. Engineer
    PREFIX: XF:31ID1-ES{ADSCANPB:01}

    TRIGGER_SIGNAL: "XF:31ID1-ES{PANDA:1}:LUT1:OUT"

    # Two below are optional parameters to include tiled support
    TILED_METADATA_URL: https://tiled.nsls2.bnl.gov/api/v1/node/metadata
    TILED_ARRAY_URL: https://tiled.nsls2.bnl.gov/api/v1/array/full
```

## Settings

| Setting                          | Required | Default | Description                                                                                                        |
| -------------------------------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------ |
| `type`                           | Yes      | -       | Must be `adscanpb`.                                                                                                |
| `environment.ENGINEER`           | Yes      | -       | Name/contact of the responsible engineer.                                                                          |
| `environment.PREFIX`             | Yes      | -       | Base PV prefix. Driver records (`ADBase`, `ADScanPB`, trigger and Tiled templates) are loaded at `$(PREFIX)cam1:`. |
| `environment.TRIGGER_SIGNAL`     | Yes      | -       | PV used as the trigger source, passed as the `TRIGGER_SIGNAL` macro to `ADScanPBTrig.template`.                    |
| `environment.TILED_METADATA_URL` | No       | -       | Tiled metadata endpoint. If set, `ADScanPBTiled.template` is loaded to enable Tiled support.                       |
| `environment.TILED_ARRAY_URL`    | No       | -       | Tiled array endpoint, passed to `ADScanPBTiled.template`. Should be set together with `TILED_METADATA_URL`.        |

## Notes

- Calls `ADScanPBConfig("$(PORT)", 0, 0, 0, 0)`, then sleeps 2 s before loading
  records. The areaDetector common plugins are loaded via `commonPlugins.cmd`.
- Tiled support is only enabled based on `TILED_METADATA_URL`; if only that is
  set, `$(TILED_ARRAY_URL)` will be undefined.
- Possible inconsistencies: `deploy_ioc` vars set no
  `deploy_ioc_device_specific_env`, so `PORT` (used by `base.cmd`) and the
  common-plugin macros (`QSIZE`, `XSIZE`, `YSIZE`, `NCHANS`, `CBUFFS`, ...) have
  no defaults and are not in `schema.yml`. No autosave req file is generated or
  registered for this role.
