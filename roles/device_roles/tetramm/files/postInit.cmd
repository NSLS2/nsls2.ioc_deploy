
# Avoid deluge of messages when debugging
#dbpf $(PREFIX)cam1:PoolUsedMem.SCAN Passive

# save things every thirty seconds
create_monitor_set("auto_settings.req", 30, "P=$(PREFIX)")
