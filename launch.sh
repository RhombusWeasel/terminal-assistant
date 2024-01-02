#!/bin/bash

set -e

source ./_term_env_/bin/activate
python3 main.py
deactivate
