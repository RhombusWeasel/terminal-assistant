#!/bin/bash

set -e

python3 -m venv _term_env_
source _term_env_/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 main.py
