#!/bin/bash

set -e

script=$(basename "$0")
version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$version" ]]
then
    echo "No Python!"
fi

parsedVersion=$(echo "${version//./}")
setVersion=$1
if [[ $parsedVersion -lt "3100" && $# -eq 0 ]]
then
    echo "Invalid python3 version, either update python3 or include the correct executable when running this script"
    echo "For example ./$script python3.10"
    exit 1
elif [[ $parsedVersion -eq "3100" || $parsedVersion -gt "3100" && $# -eq 0 ]]
then
    setVersion="python3"
fi

$setVersion -m venv _term_env_
source _term_env_/bin/activate
$setVersion -m pip install --upgrade pip
$setVersion -m pip install -r requirements.txt
$setVersion main.py
