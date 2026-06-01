# Supported Modules and Device Roles

This page lists all currently supported installable modules and deployable device roles.

!!! tip
    Generate this table locally with `make report` or `pixi run report`.

## Installable Modules

These modules can be compiled from source by the `install_module` role.

<!-- BEGIN_MODULE_TABLE -->
| Module | Versions | Type | Repository |
|--------|----------|------|------------|
| acmi2-ioc | `e815c16` | Standard | [source](https://github.com/NSLS2/acmi2-ioc) |
| ADAndor3 | `1e33769` | areaDetector | [source](https://github.com/areaDetector/adandor3) |
| ADAravis | `a0aa4d6` | areaDetector | [source](https://github.com/areaDetector/ADAravis) |
| ADCompVision | `9750d13` | areaDetector | [source](https://github.com/areaDetector/ADCompVision) |
| ADCore | `60080dc` | areaDetector | [source](https://github.com/areaDetector/ADCore) |
| ADEiger | `05e8a65` | areaDetector | [source](https://github.com/areadetector/ADEiger) |
| ADGenICam | `5d08a11` | areaDetector | [source](https://github.com/areaDetector/ADGenICam) |
| ADGermanium | `0395fac` | areaDetector | [source](https://github.com/lijibnl/test-deployment) |
| adkinetix | `aa87406` | areaDetector | [source](https://github.com/NSLS2/ADKinetix) |
| ADMerlin | `399508f` | areaDetector | [source](https://github.com/areadetector/ADMerlin) |
| admythen | `bcf2947` | areaDetector | [source](https://github.com/areaDetector/ADMythen) |
| ADPco | `b17fe13` | areaDetector | [source](https://github.com/paulscherrerinstitute/ADPco) |
| ADPhantom | `afefafc` | areaDetector | [source](https://github.com/jwlodek/ADPhantom) |
| ADPICam | `0d86fae` | areaDetector | [source](https://github.com/areaDetector/ADPICam.git) |
| ADPilatus | `72c7844` | areaDetector | [source](https://github.com/areaDetector/ADPilatus) |
| ADPluginBar | `448d96b` | areaDetector | [source](https://github.com/areaDetector/ADPluginBar) |
| ADProsilica | `9abb772` | areaDetector | [source](https://github.com/areaDetector/ADProsilica) |
| ADScanPB | `f54e2c1` | areaDetector | [source](https://github.com/NSLS2/ADScanPB.git) |
| ADSimDetector | `4b236f4` | areaDetector | [source](https://github.com/areaDetector/ADSimDetector) |
| ADSupport | `6acf83f` | areaDetector | [source](https://github.com/areaDetector/ADSupport) |
| ADTimePix3 | `2faf970` | areaDetector | [source](https://github.com/areaDetector/ADTimePix3) |
| adtucam | `c8c1685` | areaDetector | [source](https://github.com/NSLS2/ADTucam) |
| ADURL | `1c725ed` | areaDetector | [source](https://github.com/areaDetector/ADURL) |
| aduvc | `86918b6` | areaDetector | [source](https://github.com/areaDetector/ADUVC) |
| ADVimba | `34686fe` | areaDetector | [source](https://github.com/areaDetector/ADVimba) |
| ADXSPD | `986de77` | areaDetector | [source](https://github.com/NSLS2/ADXSPD) |
| BaseSNMPIOC | `6548d01` | Standard | [source](https://github.com/NSLS2/snmp-bnl) |
| BaseSoftIOC | `f4c87af` | Standard | [source](https://github.com/NSLS2/BaseSoftIOC) |
| BaseStreamIOC | `093e6cf` | Standard | [source](https://github.com/NSLS2/BaseStreamDevice) |
| caparoc | `c426a13` | Standard | [source](https://github.com/NSLS2/caparoc-ioc) |
| ek9000 | `60e62b5` | Standard | [source](https://github.com/slac-epics/ek9000) |
| elauncher | `21dede8` | Standard | [source](https://github.com/huyong1979/elauncher) |
| elio | `335730d` | Standard | [source](https://github.com/NSLS2/elio-ioc) |
| eps | `2b8896f` | Standard | [source](https://github.com/NSLS2/eps-ioc) |
| ether_ip | `b27350b` | Standard | [source](https://github.com/epics-modules/ether_ip) |
| F460 | `e24199e` | Standard | [source](https://github.com/NSLS2/F460-ioc) |
| ffmpegServer | `07c570f` | areaDetector | [source](https://github.com/jwlodek/ffmpegServer) |
| hiden_rga | `0744058` | Standard | [source](https://github.com/NSLS2/HidenRGA-ioc) |
| i400 | `0d69784` | Standard | [source](https://github.com/NSLS2/I400-ioc) |
| i404 | `4ea37d0` | Standard | [source](https://github.com/NSLS2/I404-ioc) |
| ims | `2aeddf7` | Standard | [source](https://github.com/epics-motor/motorIms) |
| linkam3 | `1093365` | Standard | [source](https://github.com/jwlodek/linkam3) |
| mcs | `49f0f2b` | Standard | [source](https://github.com/NSLS2/mcs-ioc) |
| mdrive | `8bc9a09` | Standard | [source](https://github.com/NSLS2/mdrive-ioc) |
| modbus | `bb9fa05` | Standard | [source](https://github.com/NSLS2/modbus) |
| motorpigcs2 | `a0bdeae` | Standard | [source](https://github.com/epics-motor/motorPIGCS2) |
| MotorSim | `d1d0eb8` | Standard | [source](https://github.com/epics-motor/motorMotorSim) |
| MotorSimIOC | `683afc0` | Standard | [source](https://github.com/NSLS2/motorSim-ioc) |
| MRFTiming | `3bb9fcf` | Standard | [source](https://github.com/NSLS2/MRFTiming) |
| nsls2em | `20fb70b` | areaDetector | [source](https://github.com/NSLS2/nsls2em-ioc) |
| omega_rtc | `a828c22` | Standard | [source](https://github.com/NSLS-II/omega_rtc_ioc) |
| pi3 | `2778ce0` | Standard | [source](https://github.com/NSLS2/pi3) |
| pie621 | `043ec8f` | Standard | [source](https://github.com/NSLS2/pi-e621-ioc) |
| pmac | `f811ee1` | Standard | [source](https://github.com/dls-controls/pmac) |
| ppmac | `7d627e7` | Standard | [source](https://github.com/NSLS2/ppmac) |
| pscdrv | `1ed650d` | Standard | [source](https://github.com/mdavidsaver/pscdrv) |
| QEPro | `734fbdd` | Standard | [source](https://github.com/NSLS-II/QEPro) |
| quadEM | `f5ab1e9` | areaDetector | [source](https://github.com/epics-modules/quadEM) |
| RBD9103 | `a835e1c` | Standard | [source](https://github.com/NSLS2/RBD9103) |
| snmp_bnl | `ba2b0ef` | Standard | [source](https://github.com/NSLS2/snmp-bnl) |
| SNMP-NSCL | `3cd2804` | Standard | [source](https://github.com/NSLS2/snmp-nscl) |
| std | `1b416db` | Standard | [source](https://github.com/epics-modules/std) |
| tpmac | `44274d1` | Standard | [source](https://github.com/NSLS2/tpmac) |
| va | `f4f62f6` | Standard | [source](https://github.com/nsls2/va-ioc) |
| xspress3 | `911d16d` | areaDetector | [source](https://github.com/epics-modules/xspress3) |
| zebra | `8e70cda` | Standard | [source](https://github.com/NSLS2/zebra-ioc) |
| ZPSC | `ce70f0d` | Standard | [source](https://github.com/NSLS2/zPSC.git) |
<!-- END_MODULE_TABLE -->

## Device Roles

These are the IOC types that can be deployed with `deploy_ioc`.

<!-- BEGIN_ROLE_TABLE -->
| Role | Required Module | Uses AD Common | Uses Common |
|------|----------------|----------------|-------------|
| `acmi2-ioc` | `acmi2-ioc_e815c16` | No | No |
| `adandor3` | `adandor3_1e33769` | Yes | Yes |
| `adaravis` | `adaravis_a0aa4d6` | Yes | Yes |
| `adeiger` | `adeiger_05e8a65` | Yes | Yes |
| `adgermanium` | `adgermanium_0395fac` | Yes | Yes |
| `adkinetix` | `adkinetix_aa87406` | Yes | Yes |
| `admerlin` | `admerlin_399508f` | Yes | Yes |
| `admythen` | `admythen_bcf2947` | Yes | Yes |
| `adpco` | `adpco_b17fe13` | Yes | Yes |
| `adphantom` | `adphantom_afefafc` | Yes | Yes |
| `adpicam` | `adpicam_0d86fae` | Yes | Yes |
| `adpilatus` | `adpilatus_72c7844` | Yes | Yes |
| `adprosilica` | `adprosilica_9abb772` | Yes | Yes |
| `adscanpb` | `adscanpb_f54e2c1` | Yes | Yes |
| `adsimdetector` | `adsimdetector_4b236f4` | Yes | Yes |
| `adtimepix3` | `adtimepix3_2faf970` | Yes | Yes |
| `adtucam` | `adtucam_c8c1685` | Yes | No |
| `adurl` | `adurl_1c725ed` | Yes | Yes |
| `aduvc` | `aduvc_86918b6` | Yes | Yes |
| `advimba` | `advimba_34686fe` | Yes | Yes |
| `adxspd` | `adxspd_986de77` | Yes | Yes |
| `apcpdu` | `base_snmp_ioc_6548d01` | No | Yes |
| `axis_caproto` | `—` | No | N/A (custom) |
| `base_soft_ioc` | `base_soft_ioc_f4c87af` | No | Yes |
| `bltiming` | `elauncher_21dede8` | No | N/A (custom) |
| `caparoc` | `caparoc_c426a13` | No | Yes |
| `cas_switch` | `—` | No | N/A (custom) |
| `cyberpowerpdu` | `snmp_bnl_ba2b0ef` | No | Yes |
| `elio` | `elio_335730d` | No | Yes |
| `eps` | `eps_2b8896f` | No | Yes |
| `etherip` | `ether_ip_b27350b` | No | Yes |
| `eurotherm3k` | `modbus_bb9fa05` | No | Yes |
| `f460` | `f460_e24199e` | No | Yes |
| `germcaproto` | `—` | No | N/A (custom) |
| `hiden_rga` | `hiden_rga_0744058` | No | Yes |
| `hiden_stream` | `—` | No | N/A (custom) |
| `i400` | `i400_0d69784` | No | Yes |
| `i404` | `i404_4ea37d0` | No | Yes |
| `iologik` | `modbus_bb9fa05` | No | Yes |
| `lakeshore331` | `base_stream_ioc_093e6cf` | No | Yes |
| `lakeshore336` | `base_stream_ioc_093e6cf` | No | Yes |
| `linkamt96` | `linkam3_1093365` | No | Yes |
| `mcs` | `mcs_49f0f2b` | No | Yes |
| `mdrive` | `mdrive_8bc9a09` | No | Yes |
| `motorpigcs2` | `motorpigcs2_a0bdeae` | No | Yes |
| `motorsim` | `motorsim_ioc_683afc0` | No | Yes |
| `mrftiming` | `mrftiming_3bb9fcf` | No | Yes |
| `nsls2em` | `nsls2em_20fb70b` | No | Yes |
| `omega_rtc` | `omega_rtc_a828c22` | No | Yes |
| `pandabox` | `—` | No | N/A (custom) |
| `pi-e621` | `pie621_043ec8f` | No | Yes |
| `powerpmac` | `ppmac_7d627e7` | No | Yes |
| `qepro` | `qepro_734fbdd` | No | No |
| `rbd9103` | `rbd9103_a835e1c` | No | Yes |
| `sr570` | `base_stream_ioc_093e6cf` | No | Yes |
| `stanford_dg645` | `base_stream_ioc_093e6cf` | No | Yes |
| `tektronix_afg3k` | `base_stream_ioc_093e6cf` | No | Yes |
| `tetramm` | `quadem_f5ab1e9` | No | Yes |
| `turbopmac` | `tpmac_44274d1` | No | Yes |
| `va` | `va_f4f62f6` | No | Yes |
| `wienercrate` | `snmp_nscl_3cd2804` | No | Yes |
| `xspress3` | `xspress3_911d16d` | No | Yes |
| `zebra` | `zebra_8e70cda` | No | Yes |
| `zebra_saver_caproto` | `—` | No | N/A (custom) |
| `zpsc` | `zpsc_ce70f0d` | No | Yes |
<!-- END_ROLE_TABLE -->

## Generating the Table

To regenerate the tables above from the current state of the repository:

```bash
make docs-table
```

This reads all vars files under `roles/install_module/vars/` and `roles/deploy_ioc/vars/` and writes formatted markdown tables into this file.
