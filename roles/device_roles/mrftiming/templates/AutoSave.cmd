# autosave config
set_requestfile_path("./")
set_requestfile_path("$(EPICS_MRF)/db", "")
set_pass0_restoreFile("auto_settings.sav")
set_pass1_restoreFile("auto_settings.sav")
save_restoreSet_status_prefix("OP-CT{IOC:$(IOCNAME)}")
dbLoadRecords("$(EPICS_BASE)/db/save_restoreStatus.db", "P=OP-CT{IOC:$(IOCNAME)}")
