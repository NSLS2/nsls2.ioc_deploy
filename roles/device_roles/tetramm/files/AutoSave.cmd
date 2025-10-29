
# autosave config
set_requestfile_path("./")
set_requestfile_path("$(QUADEM)/quadEMApp/Db")
set_requestfile_path("$(ADCORE)", "db")
set_requestfile_path("$(AUTOSAVE)", "db")
set_requestfile_path("$(BUSY)", "db")
set_requestfile_path("$(CALC)", "db")
set_requestfile_path("$(SSCAN)", "db")
set_requestfile_path("$(EPICS_BASE)", "req")
set_requestfile_path("$(TOP)/autosave/req")
set_savefile_path("$(TOP)/autosave/save")
set_pass0_restoreFile("auto_settings.sav")
set_pass1_restoreFile("auto_settings.sav")
save_restoreSet_status_prefix("$(PREFIX)")
dbLoadRecords("$(AUTOSAVE)/asApp/Db/save_restoreStatus.db", "P=$(PREFIX)")

epicsEnvSet("BUILT_SETTINGS", "$(TOP)/autosave/req/built_settings.req")
autosaveBuild("$(BUILT_SETTINGS)", "_settings.req", 1)
