import boto3
import datetime
import time
import pytz
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description='Create an RDS snapshot and removes older ones based on specifications.')
parser.add_argument('-p', '--profile', help='The AWS Profile to use for the backup', required=True)
parser.add_argument('-i', '--instance', help='The AWS RDS instance to backup', required=True)
parser.add_argument('-x', '--prefix', help='The prefix to be used for the snapshot', required=True)
parser.add_argument('-r', '--retention', help='The number of days to retain the backup', type=int, required=True)
args = parser.parse_args()



# Settings
aws_profile = args.profile
rds_instance = args.instance
backup_name_prefix = args.prefix
backup_retention = args.retention
# ------

# Constants
current_timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

# Prepare AWS Session
session = boto3.Session(profile_name=aws_profile)
client = session.client('rds')

# View RDS Instance
response = client.describe_db_instances(
    DBInstanceIdentifier = rds_instance
)
for instances in response['DBInstances']:
    print "RDS Instance: %s" % instances['DBInstanceIdentifier']


snapshot_name = str(backup_name_prefix + rds_instance + "-" + current_timestamp)
print "RDS Snapshot: %s..." % snapshot_name

response = client.create_db_snapshot(
    DBSnapshotIdentifier=snapshot_name,
    DBInstanceIdentifier=rds_instance
)

print "RDS Snapshot: Processing..."
while True:
    response = client.describe_db_snapshots(
        DBSnapshotIdentifier=snapshot_name,
        DBInstanceIdentifier=rds_instance,
        SnapshotType='manual'
    )
    current_status = response['DBSnapshots'][0]['Status']
    if current_status != 'available':
        print "RDS Snapshot: Status - %s" % current_status
        time.sleep(60)
    else:
        break

print "RDS Snapshot: Cleaning..."
# Find old RDS Snapshots
response = client.describe_db_snapshots(
    DBInstanceIdentifier=rds_instance,
    SnapshotType='manual'
)

for snapshots in response['DBSnapshots']:
    if snapshots['SnapshotCreateTime'] < pytz.utc.localize(datetime.datetime.utcnow()) - \
            datetime.timedelta(days=backup_retention):
        snapshot_to_delete = snapshots['DBSnapshotIdentifier']
        print "RDS Snapshot: - %s" % snapshot_to_delete
        response = client.delete_db_snapshot(
            DBSnapshotIdentifier=snapshot_to_delete
        )

print "RDS Snapshot: Complete..."
