export PYTHONPATH=$(dirname $0)/../
python $PYTHONPATH/dmgweb_packages/application.py build
mv build/index.html build/index
