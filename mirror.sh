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
MIRROR_DIR=$(dirname $0)
cd $MIRROR_DIR

echo "Generate the static website..."
export PYTHONPATH=$MIRROR_DIR/../
python $PYTHONPATH/dmgweb_packages/application.py build

echo "Do a copy of the json files just in case we loose the master ones..."
mkdir -p $MIRROR_DIR/mirror/save_json/
cp $MIRROR_DIR/data/*json $MIRROR_DIR/mirror/save_json/ 

echo "Rename index.html as index..."
mv $MIRROR_DIR/mirror/index.html $MIRROR_DIR/mirror/index

echo "Remove old mirror..."
rm -f $MIRROR_DIR/data/mirror.tgz

echo "Create data/mirror.tgz..."
tar cvzf $MIRROR_DIR/data/mirror.tgz $MIRROR_DIR/mirror

echo "Remove mirror folder..."
rm -Rf $MIRROR_DIR/mirror

echo "Finished :)"

cd $OLDPWD
