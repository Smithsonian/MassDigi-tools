#!/usr/bin/env bash

folder=$1

# source venv/bin/activate
# python3 -m pip install -U pip
# python3 -m pip install -U -r requirements.txt

./jpc_generate_hmo_auto.py $folder

./id_manager.py $folder

./hmo_to_arches.py $folder

# deactivate
