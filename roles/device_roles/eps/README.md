# eps

Deploys an IOC for a beamline Equipment Protection System (EPS) Allen-Bradley
PLC, communicating over EtherNet/IP via the `ether_ip` driver. PLC tags (gate
valves, shutters, interlocks, thermocouples, flow meters, etc.) are mapped to
PVs through user-defined substitutions using the EPS database templates. The IOC
is built from [eps-ioc](https://github.com/NSLS2/eps-ioc) (version `afbfea3`).

## Example Configuration

Taken from [`examples/eps-01/config.yml`](examples/eps-01/config.yml):

```yaml
eps-01:
  type: eps
  environment:
    ENGINEER: "C. Engineer"
    PREFIX: XF:31ID1-ES{EPS:01}
    PLC: "XF31ID1_EPS"
    PLC_IP: "xf31id1-plc1.nsls2.bnl.gov"
    ACF: "/epics/common/bl-cas/31id/eps.acf"

  substitutions:
    plc-va:
      template_macros: "PLC=$(PLC)"
      templates:
        - filepath: "$(EPS)/db/plc-va-gv.template"
          pattern: ["Sys", "Dev", "Tag"]
          instances:
            - ["XF:09IDA-VA", "Fltr:1-GV:1", "IDA_VA_GVA"]
            - ["XF:09IDA-VA", "Mono:DMM-GV:1", "IDA_VA_GVB"]

        - filepath: "$(EPS)/db/plc-bi.template"
          pattern: ["Sys", "Dev", "Sig", "DESC", "Tag", "Rate", "ZNAM", "ONAM", "ZSV", "OSV"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:Vac-Sts", "Main FE Sh interlock(vacuum)", "Misc_Sts_1[0]", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-EPS", "IL:PSh1", "Main:Vac-Sts", "Main PSh1 interlock(vacuum)", "Misc_Sts_1[1]", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-EPS", "IL:PSh2", "Main:Vac-Sts", "Main PSh2 interlock(vacuum)", "Misc_Sts_1[2]", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-VA", "Handshake:1", "BL:Vac-Sts", "BL Vacuum status", "Misc_Sts_1[3]", "1", "Alarm", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-VA", "Handshake:1", "FE:Vac-Sts", "FE Vacuum status", "Misc_Sts_1[4]", "1", "Alarm", "OK", "MAJOR", "NO_ALARM"]

        - filepath: "$(EPS)/db/plc-first.template"
          pattern: ["Sys", "Dev", "Sig", "Seq", "ArrNum"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:Vac", "1", "0"]
            - ["XF:09ID-EPS", "IL:PSh1", "Main:Vac", "1", "1"]
            - ["XF:09ID-EPS", "IL:PSh2", "Main:Vac", "1", "2"]

            - ["XF:09ID-EPS", "Handshake:1", "BL:Vac", "1", "3"]
            - ["XF:09ID-EPS", "Handshake:1", "FE:Vac", "1", "4"]

        - filepath: "$(EPS)/db/plc-va-rly.template"
          pattern: ["Sys", "Dev", "Mod", "Seq", "ArrNum"]
          instances:
            - ["XF:09IDA-VA", "Msk:WB-CCG:1", "CCG", "0", "0"]
            - ["XF:09IDA-VA", "Msk:WB-TCG:1", "TCG", "0", "0"]

            - ["XF:09IDA-VA", "Fltr:DM1-CCG:1", "CCG", "0", "1"]
            - ["XF:09IDA-VA", "Fltr:DM1-TCG:1", "TCG", "0", "1"]

    plc-pps:
      template_macros: "PLC=$(PLC)"
      templates:
        - filepath: "$(EPS)/db/plc-pps-sh.template"
          pattern: ["Sys", "Dev", "ShTag"]
          instances:
            - ["XF:09IDA-PPS", "Sh:FE", "FE_SH"]
            - ["XF:09IDA-PPS", "PSh:1", "L1S1_SH"]
            - ["XF:09IDA-PPS", "PSh:2", "L1S3_SH"]

        - filepath: "$(EPS)/db/plc-bi.template"
          pattern: ["Sys", "Dev", "Sig", "DESC", "Tag", "Rate", "ZNAM", "ONAM", "ZSV", "OSV"]
          instances:
            - ["XF:09ID-EPS", "", "Out:ExpIntlk-Sts", "Experiment(User) Interlock", "Misc_Sts_0[0]", "1", "Interlocked", "Ready", "MAJOR", "NO_ALARM"]

    plc-ts:
      template_macros: "PLC=$(PLC)"
      templates:
        - filepath: "$(EPS)/db/plc-tc.template"
          pattern: ["Sys", "Dev", "Seq", "ArrNum", "DESC"]
          instances:
            - ["XF:09IDA-OP:1", "Fltr:DM1-TC:1", "0", "0", "Harmonic Fltr1"]
            - ["XF:09IDA-OP:1", "Fltr:DM1-TC:2", "0", "1", "Harmonic Fltr2"]

        - filepath: "$(EPS)/db/plc-tc.template"
          pattern: ["Sys", "Dev", "Seq", "ArrNum", "DESC"]
          instances:
            - ["XF:09IDA-OP:1", "Msk:WB-RTD:UT", "1", "0", "Mask US Upper"]
            - ["XF:09IDA-OP:1", "Msk:WB-RTD:UB", "1", "1", "Mask US Lower"]

        - filepath: "$(EPS)/db/plc-bi.template"
          pattern: ["Sys", "Dev", "Sig", "DESC", "Tag", "Rate", "ZNAM", "ONAM", "ZSV", "OSV"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:T-Sts", "Main FE Sh interlock(T)", "", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-EPS", "IL:PSh1", "Main:T-Sts", "Main PSh1 interlock(T)", "", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-EPS", "IL:PSh2", "Main:T-Sts", "Main PSh2 interlock(T)", "", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]

        - filepath: "$(EPS)/db/plc-first.template"
          pattern: ["Sys", "Dev", "Sig", "Seq", "ArrNum"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:T", "", ""]
            - ["XF:09ID-EPS", "IL:PSh1", "Main:T", "", ""]
            - ["XF:09ID-EPS", "IL:PSh2", "Main:T", "", ""]

    plc-wtr:
      template_macros: "PLC=$(PLC)"
      templates:
        - filepath: "$(EPS)/db/plc-va-gv.template"
          pattern: ["Sys", "Dev", "Tag", "ASG"]
          instances:
            - ["XF:09IDA-PU", "DI-Supply:IV", "", "EPSEXPERT"]
            - ["XF:09IDA-PU", "DI-Return:IV", "", "EPSEXPERT"]
            - ["XF:09IDA-PU", "PCW-Supply:IV", "", "EPSEXPERT"]
            - ["XF:09IDA-PU", "PCW-Return:IV", "", "EPSEXPERT"]

        - filepath: "$(EPS)/db/plc-pt.template"
          pattern: ["Sys", "Dev", "Seq", "ArrNum", "ESLO", "EGU", "PREC", "EOFF", "AOFF"]
          instances:
            - ["XF:09IDA-PU", "DI-Supply", "", "", "0.009375", "PSIG", "0", "0", "-4000"]
            - ["XF:09IDA-PU", "DI-Return", "", "", "0.009375", "PSIG", "0", "0", "-4000"]

            - ["XF:09IDB-PU", "DI-Supply", "", "", "0.009375", "PSIG", "0", "0", "-4000"]
            - ["XF:09IDB-PU", "DI-Return", "", "", "0.009375", "PSIG", "0", "0", "-4000"]

            - ["XF:09IC-PU", "DI-Supply", "", "", "0.009375", "PSIG", "0", "0", "-4000"]
            - ["XF:09IC-PU", "DI-Return", "", "", "0.009375", "PSIG", "0", "0", "-4000"]

        - filepath: "$(EPS)/db/plc-fm.template"
          pattern: ["Sys", "Dev", "Seq", "ArrNum", "ESLO", "EGU", "PREC", "EOFF", "AOFF"]
          instances:
            - ["XF:09IDA-OP:1", "Msk:WB-PPS:1A", "", "", "0.003125", "GPM", "2", "0.0", "-4000"]
            - ["XF:09IDA-OP:1", "Msk:WB-PPS:1B", "", "", "0.003125", "GPM", "2", "0.0", "-4000"]

        - filepath: "$(EPS)/db/plc-bi.template"
          pattern: ["Sys", "Dev", "Sig", "DESC", "Tag", "Rate", "ZNAM", "ONAM", "ZSV", "OSV"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:Wtr-Sts", "Main FE Sh interlock(water)", "", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]
            - ["XF:09ID-EPS", "IL:PSh1", "Main:Wtr-Sts", "Main PSh1 interlock(water)", "", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]

            - ["XF:09IDA-PU", "Hutch-LD:1", "Alarm-Sts", "A-Hutch Leak Det Status", "", "1", "Leak", "NO Leak", "MAJOR", "NO_ALARM"]

        - filepath: "$(EPS)/db/plc-first.template"
          pattern: ["Sys", "Dev", "Sig", "Seq", "ArrNum"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:Wtr", "", ""]
            - ["XF:09ID-EPS", "IL:PSh1", "Main:Wtr", "", ""]

            - ["XF:09IA-PU", "DI-Supply:IV", "Pos", "", ""]
            - ["XF:09IA-PU", "DI-Return:IV", "Pos", "", ""]

    plc-ln2:
      template_macros: "PLC=$(PLC)"
      templates:
        - filepath: "$(EPS)/db/plc-va-gv.template"
          pattern: ["Sys", "Dev", "Tag", "ASG"]
          instances:
            - ["XF:09IDA-PU", "LN2-Main:IV", "", "EPSEXPERT"]
            - ["XF:09IDA-PU", "LN2-Cryo:IV", "", "EPSEXPERT"]
            - ["XF:09IDA-PU", "LN2-FOE:IV", "", "EPSEXPERT"]

        - filepath: "$(EPS)/db/plc-bi.template"
          pattern: ["Sys", "Dev", "Sig", "DESC", "Tag", "Rate", "ZNAM", "ONAM", "ZSV", "OSV"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:LN2-Sts", "Main FE Sh interlock(LN2)", "", "1", "Interlocked", "OK", "MAJOR", "NO_ALARM"]

            - ["XF:09IDA-PU", "LN2-Main:IV", "EStop-Sts", "LN2 Main Supply Emergency Stop", "", "1", "Pressed", "NO Pressed", "MINOR", "NO_ALARM"]
            - ["XF:09IDA-OP", "Cryo:1", "Alarm-Sts", "Cryocooler alarm status", "", "1", "Alarm", "OK", "MINOR", "NO_ALARM"]
            - ["XF:09IDA-OP", "Cryo:1", "Run-Sts", "Cryocooler run status", "", "1", "Not Running", "Running", "MINOR", "NO_ALARM"]
            - ["XF:09IDA-OP", "Cryo:1", "Inh-Sts", "Cryocooler inhibit status", "", "1", "Inhibited", "Not Inhibited", "MINOR", "NO_ALARM"]

        - filepath: "$(EPS)/db/plc-first.template"
          pattern: ["Sys", "Dev", "Sig", "Seq", "ArrNum"]
          instances:
            - ["XF:09ID-EPS", "IL:FE", "Main:LN2", "", ""]
            - ["XF:09IDA-OP", "Cryo:1", "Run", "", ""]
```

## Settings

| Setting                                      | Required | Default | Description                                                                                                                                                                                                 |
| -------------------------------------------- | -------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`                                       | Yes      | -       | Must be `eps`.                                                                                                                                                                                              |
| `environment.ENGINEER`                       | Yes      | -       | Name/contact of the responsible engineer.                                                                                                                                                                   |
| `environment.PREFIX`                         | Yes      | -       | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster).                                                                                                                                      |
| `environment.PLC`                            | No*      | -       | Name of the PLC passed to `drvEtherIP_define_PLC`; typically passed to templates via `template_macros: "PLC=$(PLC)"`.                                                                                       |
| `environment.PLC_IP`                         | No*      | -       | IP address or hostname of the PLC.                                                                                                                                                                          |
| `environment.ACF`                            | No*      | -       | Path to the EPICS access security file, loaded with `asSetFilename` (used e.g. for the `EPSEXPERT` access security group).                                                                                  |
| `substitutions`                              | No       | -       | Map of substitutions file name to its contents. Each entry generates `$(TOP)/db/<name>.substitutions`, loaded with `dbLoadTemplate` in `common.cmd`.                                                        |
| `substitutions.<name>.template_macros`       | No       | -       | Macro string passed as the second argument to `dbLoadTemplate` (e.g. `"PLC=$(PLC)"`).                                                                                                                       |
| `substitutions.<name>.templates`             | No       | -       | List of templates in the generated substitutions file.                                                                                                                                                      |
| `substitutions.<name>.templates[].filepath`  | Yes      | -       | Path of the database template, e.g. `$(EPS)/db/plc-bi.template`. Available EPS templates used in the example: `plc-va-gv`, `plc-bi`, `plc-first`, `plc-va-rly`, `plc-pps-sh`, `plc-tc`, `plc-pt`, `plc-fm`. |
| `substitutions.<name>.templates[].pattern`   | Yes      | -       | List of macro names forming the substitutions `pattern` row.                                                                                                                                                |
| `substitutions.<name>.templates[].instances` | Yes      | -       | List of instances; each is a list of values matching `pattern`.                                                                                                                                             |

\* Not in `schema.yml`, but referenced unconditionally by `iocBoot/base.cmd`, so
they must be set for the IOC to work.

## Notes

- Generates `iocBoot/base.cmd`, which sets `EIP_buffer_limit(492)`, initializes
  the EtherIP driver, defines the PLC with
  `drvEtherIP_define_PLC("$(PLC)", "$(PLC_IP)", 0)` (slot 0), sets
  `EIP_verbosity(6)`, and loads the access security file `$(ACF)`.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- `PLC`, `PLC_IP`, and `ACF` are used by the role but are not declared in
  `schema.yml`.
