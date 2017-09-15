export PYTHONPATH=$(dirname $(dirname $(realpath $0)))
touch /tmp/www-packages.sock ; chmod 777 /tmp/www-packages.sock
uwsgi -s /tmp/www-packages.sock --chmod-socket=777 --processes 10 --pythonpath $PYTHONPATH --manage-script-name --mount /=application:app
