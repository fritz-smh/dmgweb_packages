#!/bin/bash
#
# dmgweb_packages
#
# This script is used to generate a static mirror of the website. 
# The mirror will be generated in the ./mirror/ folder.
# Then, a tgz is done for publication and is stored as ./data/mirror.tgz
# This tgz is directly available from the root website
#
# Run this script as : 
# /path/to/mirror.sh > /path/to/log/dmgweb_package_mirror_$(date "+%Y%m%d_%H%M").log

OLDPWD=$PWD
MIRROR_DIR=$(dirname $(realpath $0))
BACKUP_DIR=$MIRROR_DIR/backup/
cd $MIRROR_DIR

echo "Generate the static website..."
export PYTHONPATH=$(dirname $MIRROR_DIR/)
python $PYTHONPATH/dmgweb_packages/application.py build

echo "Do a copy of the json files just in case we loose the master ones..."
mkdir -p $MIRROR_DIR/mirror/save_json/
cp $MIRROR_DIR/data/*json $MIRROR_DIR/mirror/save_json/ 

echo "Rename index.html as index..."
mv $MIRROR_DIR/mirror/index.html $MIRROR_DIR/mirror/index

echo "Remove old mirror..."
rm -f $MIRROR_DIR/data/mirror.tgz

echo "Create data/mirror.tgz..."
#tar cvzf $MIRROR_DIR/data/mirror.tgz $MIRROR_DIR/mirror
cd $MIRROR_DIR/mirror
tar cvzf $MIRROR_DIR/data/mirror.tgz *

echo "Remove mirror folder..."
rm -Rf $MIRROR_DIR/mirror

echo "Generate backup..."
NOW=$(date "+%Y%m%d_%H%M")
mkdir -p $BACKUP_DIR
cp -p $MIRROR_DIR/data/mirror.tgz $BACKUP_DIR/mirror-backup-$NOW.tgz

echo "Finished :)"

cd $OLDPWD
