
# save things every thirty seconds
create_monitor_set("auto_settings.req", 30, "P=$(PREFIX)")

dbl > /tmp/{{ ioc_name }}-records.dbl
date
