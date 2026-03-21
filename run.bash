#!/usr/bin/bash

if [ ! -d .venv ]; then
    python -m venv .venv
fi 

source .venv/bin/activate
python3 -m ensurepip --upgrade
pip install -r requirements.txt

export PORT=8080
#python src/main.py
export PYTHONPATH=./src
#flask --app main  run --port 8080
python -m flask  --app  main:app run --port 8080 --host 0.0.0.0
#gunicorn --chdir ./src --bind 0.0.0.0:8080 main:app



