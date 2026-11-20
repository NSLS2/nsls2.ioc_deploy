# cyberpowerpdu

Deploys an SNMP-based IOC for monitoring and controlling CyberPower power distribution units (PDUs), including per-outlet naming and on/off/reboot control. The IOC is built from [snmp-bnl](https://github.com/NSLS2/snmp-bnl) (version `ba2b0ef`).

## Example Configuration

Taken from [`examples/cyberpowerpdu-01/config.yml`](examples/cyberpowerpdu-01/config.yml):

```yaml
cyberpowerpdu-01:
  type: cyberpowerpdu
  environment:
    SYS: "XF:31ID-CT"
    DEV: "{PDU:3}"
    IP: "127.0.0.1"
    PREFIX: XF:31ID1-ES{PDU:3}
    CT_PREFIX: $(SYS)$(DEV)
    ENGINEER: "J. Wlodek"
  num_outlets: 8
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `cyberpowerpdu`. |
| `num_outlets` | Yes | - | Number of PDU outlets; one set of outlet records (`cyberPDU_Outlet.template`) is generated for each outlet `1..num_outlets`. |
| `environment.SYS` | Yes | - | System portion of the device PV prefix (`$(SYS)$(DEV)`). |
| `environment.DEV` | Yes | - | Device portion of the device PV prefix (including braces, e.g. `{PDU:3}`). |
| `environment.IP` | Yes | - | IP address or hostname of the PDU, used as the SNMP target for all records. |
| `environment.PREFIX` | Yes | - | IOC-level PV prefix; used for iocStats/autosave/reccaster PVs only if `CT_PREFIX` is not defined. |
| `environment.CT_PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). Takes precedence over `PREFIX`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |
| `environment.SNMP` | No | `/epics/modules/snmp-bnl` | Path to the snmp-bnl module. |

## Notes

- Copies the CyberPower MIB (`CyberPower_MIB_v2.11.MIB`) and SNMPv2 MIBs into `$(TOP)/mibs`, and sets `MIBDIRS` to include it along with the system SNMP MIB directories.
- Records use the SNMP community `private`.
- Generates `db/cyberpdu.substitutions` (PDU-level records such as load current) and `db/cyberpdu_outlet.substitutions` (per-outlet name/control/status records), loaded from `iocBoot/base.cmd`.
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- Since `CT_PREFIX` takes precedence, `PREFIX` is effectively unused when both are set (as in the example), though the schema requires both.
