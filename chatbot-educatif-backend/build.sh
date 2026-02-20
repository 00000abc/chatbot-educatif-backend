#!/usr/bin/env bash
set -o errexit

pip install -r chatbot-educatif-backend/requirements.txt
python chatbot-educatif-backend/manage.py collectstatic --no-input
python chatbot-educatif-backend/manage.py migrate
