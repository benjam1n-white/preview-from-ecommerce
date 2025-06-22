#!/bin/bash
pip install -r requirements.txt
if [-d "static"]; then
    python manage.py collectstatic --noinput
fi
python manage.py migrate
