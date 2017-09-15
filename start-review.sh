export PYTHONPATH=$(dirname $(dirname $(realpath $0)))
python $PYTHONPATH/dmgweb_packages/review.py $*
