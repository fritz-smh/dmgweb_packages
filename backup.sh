#!/bin/bash
#
# Local backup script
#
#

PWD=$(dirname $(realpath $0))
BACKUP_DIR=$PWD/backup/


if [[ ! -d $BACKUP_DIR ]] ; then
    echo "Create backup dir : $BACKUP_DIR"
    mkdir -p $BACKUP_DIR
else
    echo "Backup dir already exists : $BACKUP_DIR"
fi


tar cvzf $BACKUP_DIR/backup_packages_$(date "+%Y%m%d-%H%M%S").tgz $PWD/data/

echo "End!"
