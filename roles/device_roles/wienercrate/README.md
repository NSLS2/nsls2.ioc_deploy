# wienercrate

This role deploys an EPICS IOC for monitoring and controlling Wiener power supply crates via SNMP. The IOC is built from [SNMP-NSCL](https://github.com/NSLS2/snmp-nscl) (version `3cd2804`).

## Example Configuration

Taken from [`example.yml`](example.yml):

```yaml
wps1:
  type: wienercrate

  # NOTE: the PVs for installed power supply cards are defined in the
  # substitution file in Db/<ioc-name> directory. The file may be either
  # regular substitution file 'supplies.substitutions' or Jinja template
  # 'supplies.substitution.j2'. The rows of the file depend on the number
  # and types of the installed cards. Look for the installed IOC to find
  # examples of the template.

  # SYS and DEV: used to generate prefix for each device
  # WIENER_IP may be an IP address or host name
  environment:
    SYS: "XF:18IDB-OP"
    DEV: "WPS:01"
    WIENER_IP: "10.66.138.60"

    # PREFIX is used for common IOC PVs
    PREFIX: $(SYS){IOC:SNMP}
    ENGINEER: "D. Gavrilov"
```

## Settings

| Setting | Required | Default | Description |
|---|---|---|---|
| `type` | Yes | - | Must be `wienercrate`. |
| `environment.SYS` | Yes | - | System portion of the crate PV prefix (`P` macro of `wienerCrate.db`). |
| `environment.DEV` | Yes | - | Device portion of the crate PV prefix; crate PVs are `$(SYS){$(DEV)}...`. |
| `environment.WIENER_IP` | Yes | - | IP address or hostname of the crate's SNMP interface (`CRATE` macro). |
| `environment.PREFIX` | Yes | - | PV prefix for IOC-specific PVs (iocStats, autosave status, reccaster). May reference other variables, e.g. `$(SYS){IOC:SNMP}`. |
| `environment.ENGINEER` | Yes | - | Name/contact of the responsible engineer. |

## Notes

- Installs `mibs/WIENER-CRATE-MIB.txt` and copies `db/wienerCrate.db` (crate-level PVs) and `db/supplies.db` (per-output-channel PVs, macros `P`, `R`, `CRATE`, `TYPE`, `CHAN`, `SCAN`) into the IOC directory. Requires the `net-snmp` and `net-snmp-devel` packages (installed with the module).
- `base.cmd` loads `$(TOP)/db/wienerCrate.db` and then `dbLoadTemplate("$(TOP)/db/supplies.substitutions")`. The role does **not** generate `supplies.substitutions`; it must be supplied separately, with rows that depend on the number and type of installed power supply cards (see the comment in the example).
- `makeAutosaveFilesFromDbInfo()` is enabled for this IOC type.
- The databases use `%(WCR_PREF)` (documented in `wienerCrate.db` as `WCR_PREF="guru WIENER-CRATE-MIB::"`), but neither `WCR_PREF` nor `MIBDIRS` is set by the role or allowed by the schema; ensure they are defined for the IOC to resolve the MIB.
