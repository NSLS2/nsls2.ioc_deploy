# adgermanium

Deploys an areaDetector IOC for a germanium detector, exposing MCA, TDC,
spectrum, and intensity arrays through `NDStdArrays` plugins. The IOC is built
from [ADGermanium](https://github.com/lijibnl/test-deployment) (version
`0395fac`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
adgermanium-01:
  type: adgermanium
  environment:
    ENGINEER: Ji Li
    PREFIX: XF:31ID1-ES{ADGERMANIUM:01}
    DETECTOR_IP: 172.16.0.1
    NELM: 384
```

## Settings

| Setting                   | Required | Default | Description                                                                                                                                                 |
| ------------------------- | -------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                    | Yes      | -       | Must be `adgermanium`.                                                                                                                                      |
| `environment.ENGINEER`    | Yes      | -       | Name of the responsible engineer; set as an IOC environment variable.                                                                                       |
| `environment.PREFIX`      | Yes      | -       | Base PV prefix for the detector and array plugin records.                                                                                                   |
| `environment.DETECTOR_IP` | Yes      | -       | IP address of the detector, passed to `germaniumConfig`.                                                                                                    |
| `environment.NELM`        | Yes      | -       | Number of detector elements (channels). Passed to `germaniumConfig` and used as the Y size of the MCA and TDC arrays and the X size of the intensity array. |

## Notes

- The IOC executable is `germanium`. `epicsEnv.cmd` defines fixed array ports
  (`GERM`, `ARR_MCA`, `ARR_TDC`, `ARR_SPCT`, `ARR_INTENS`), asyn addresses 0-4,
  and array sizes (MCA X size `4096`, TDC X size `1024`).
- Array plugins are loaded with `R=MCA:`, `R=TDC:`, `R=SPCT:`, and `R=INTENS:`
  under `PREFIX`.
- The role does not set default `PORT` or `QSIZE` values. `germaniumConfig` and
  the areaDetector `commonPlugins.cmd` reference `$(PORT)`, while the detector
  database uses the fixed port name `GERM`.
