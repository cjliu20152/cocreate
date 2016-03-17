#!/bin/sh
export DJANGO_SETTINGS_MODULE="cocreate.settings"
echo 'Deleting db.sqlite3'
rm ./db.sqlite3

echo 'Making new migrations'
./manage.py makemigrations

echo 'Running manage.py migrate'
./manage.py migrate

echo 'Creating superuser cocreate'
./manage.py createsuperuser --noinput --username cocreate --email=bkeyes@mitre.org

echo 'Setting cocreate password'
./setCoCreatePassword.py cocreate

echo 'Loading fixtures'
./manage.py loaddata cocreate/fixtures/sandbox_templates.json
