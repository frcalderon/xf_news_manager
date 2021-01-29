#!/usr/bin/env bash

env="venv"

python3 -m venv ${env}

source ${env}/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

deactivate