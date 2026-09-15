# save things every thirty seconds
create_monitor_set("auto_settings.req", 30, "P=$(P), R=$(R)")
#create_manual_set("evr01_preset.req", "P=$(P),R=$(R):,CONFIGMENU=1")

# update settings
dbpf $(P)$(R)DBus:Status.PROC 1
dbpf $(P)$(R)PulseGen0:Status.PROC 1
