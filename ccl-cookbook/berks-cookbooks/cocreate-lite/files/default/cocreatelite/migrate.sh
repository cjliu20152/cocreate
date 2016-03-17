#!/bin/bash

{
source env/bin/activate
python3.4 manage.py migrate
} || {
python3.4 manage.py migrate
} || {
python3.4 manage.py syncdb --noinput
python3.4 manage.py migrate
} || {
python3.4 manage.py makemigrations
python3.4 manage.py migrate
} || {
python3.4 manage.py -h
python3.4 manage.py migrate
}
exit 0
