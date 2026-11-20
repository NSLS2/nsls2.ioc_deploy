# motorpigcs2

Deploys an IOC for PI (Physik Instrumente) GCS2 motor controllers using the Motor module, communicating over TCP/IP. The IOC is built from [motorPIGCS2](https://github.com/epics-motor/motorPIGCS2) (version `a0bdeae`).

## Example Configuration

Taken from [`examples/motorpigcs2-01/config.yml`](examples/motorpigcs2-01/config.yml):

```yaml
motorpigcs2-01:
  type: motorpigcs2
  environment:
    ENGINEER: "J. MA"
    PORT: "GCS2"
    ASYN_PORT: "GCS2_ETH"
    P: "XF:31ID-ES"
    R: "{GCS2:1}"
    PREFIX: "$(P)$(R)"
    CT_PREFIX: "XF:31ID-CT{GCS2:1}"
    CONTROLLER_IP: "10.66.xx.xx"
    CONTROLLER_PORT: 50000
  axes:
    - suffix: "{Gon:1-Ax:XP}Mtr"
      addr: 0
      desc: "Fine Motion X"
      egu: "um"
      dir: "Pos"
      velo: 5
      vbas: 0
      accl: 0.2
      bdst: 0
      bvel: 1
      bacc: 0.2
      mres: 0.0001
      prec: 4
      dhlm: 0
      dllm: 0
      init: ""
    - suffix: "{Gon:1-Ax:YP}Mtr"
      addr: 1
      desc: "Fine Motion Y"
      egu: "um"
      dir: "Pos"
      velo: 5
      vbas: 0
      accl: 0.2
      bdst: 0
      bvel: 1
      bacc: 0.2
      mres: 0.0001
      prec: 4
      dhlm: 0
      dllm: 0
      init: ""
    - suffix: "{Gon:1-Ax:ZP}Mtr"
      addr: 2
      desc: "Fine Motion Z"
      egu: "um"
      dir: "Pos"
      velo: 5
      vbas: 0
      accl: 0.2
      bdst: 0
      bvel: 1
      bacc: 0.2
      mres: 0.0001
      prec: 4
      dhlm: 0
      dllm: 0
      init: ""
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `motorpigcs2`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.PORT` | Yes | - | asyn port name of the `PI_GCS2_CreateController` motor driver. |
| `environment.ASYN_PORT` | Yes | - | Name of the underlying asyn IP port. |
| `environment.P` | Yes | - | PV prefix for motor records and `motorUtil.db` (allstop/alldone). |
| `environment.R` | Yes | - | Second part of the device prefix (used in `PREFIX`). |
| `environment.PREFIX` | Yes | - | Device prefix, typically `$(P)$(R)`. |
| `environment.CT_PREFIX` | Yes | - | IOC prefix for the troubleshooting asyn record (`$(CT_PREFIX)Asyn`), iocAdmin, autosave status and reccaster records. |
| `environment.CONTROLLER_IP` | Yes | - | IP address or hostname of the controller. |
| `environment.CONTROLLER_PORT` | Yes | `50000` | TCP port of the controller (1-65535). |
| `environment.MOTOR_PIGCS2` | No | `/epics/modules/motorPIGCS2` | Path to the motorPIGCS2 module. |
| `axes` | Yes | - | List of motor axes; one `motorgcs2.template` instance each. |
| `axes[].suffix` | Yes | - | Motor record name suffix (`M`); the PV is `$(P)<suffix>`. |
| `axes[].addr` | Yes | - | Axis address on the controller (asyn `ADDR`). |
| `axes[].desc` | Yes | - | Motor description (`DESC`). |
| `axes[].egu` | Yes | - | Engineering units (`EGU`). |
| `axes[].dir` | Yes | - | Direction (`DIR` macro). |
| `axes[].velo` | Yes | - | Velocity (`VELO`). |
| `axes[].vbas` | Yes | - | Base velocity (`VBAS`). |
| `axes[].accl` | Yes | - | Acceleration time (`ACCL`). |
| `axes[].bdst` | Yes | - | Backlash distance (`BDST`). |
| `axes[].bvel` | Yes | - | Backlash velocity (`BVEL`). |
| `axes[].bacc` | Yes | - | Backlash acceleration (`BACC`). |
| `axes[].mres` | Yes | - | Motor resolution (`MRES`, also used as `RDBD`). |
| `axes[].prec` | Yes | - | Display precision (`PREC`). |
| `axes[].dhlm` | Yes | - | Dial high limit (`DHLM` macro). |
| `axes[].dllm` | Yes | - | Dial low limit (`DLLM` macro). |
| `axes[].init` | Yes | - | Init string (`INIT` macro). |

## Notes

- Generates `iocBoot/base.cmd` and `db/motorgcs2.substitutions`, and copies `files/motorgcs2.template` to `db/`.
- Copies `files/Makefile` into the installed module's `pigcs2App/src` directory to build the `pigcs2` IOC with devIocStats and autosave support (module built with `BUILD_IOCS=YES`).
- `PI_GCS2_CreateController` is called with a fixed `numAxes` of `3` and moving/idle poll periods of 100/1000 ms, regardless of the number of `axes`. asyn tracing is enabled on `ASYN_PORT` during controller creation and reduced afterwards.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- Possible issues:
  - `motorgcs2.template` does not use the `DIR`, `DHLM`, `DLLM` or `INIT` macros, so those axis settings currently have no effect; `VMAX` is not configurable and defaults to `0.5`.
  - `templates/motorgcs2.substitutions.j2` has `{% endfor -%}}`, which emits an extra `}` in the generated substitutions file.
  - The module is skipped in compilation tests because it fails to compile at the pinned commit (per `verify.yml`).
