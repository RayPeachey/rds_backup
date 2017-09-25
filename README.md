# RDS Backup

This script initiates a manual snapshot of an RDS instance. Additionally, this will include enforcing the retention policy at the end of the script execution.

# Required Parameters
Parameter Short | Parameter Long | Description
--- | --- | ---
-p | --profile | The AWS Profile to use for the backup
-i | --instance | The AWS RDS instance to backup
-x | --prefix | The prefix to be used for the name of the snapshot
-r | --retention | The number of days to retain the backup

