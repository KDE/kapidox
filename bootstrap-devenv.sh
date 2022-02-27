#!/usr/bin/env bash

set -e

if ! [ -d "kapidox" ]; then
  echo "FATAL: this must be executed in the root of the kapidox project"
  exit 1
fi

python3 -m venv .kapidox_venv
source .kapidox_venv/bin/activate
pip3 install --upgrade pip wheel
pip3 install -r requirements.frozen.txt
pip3 install --no-deps --editable .

echo "******************************************************************"
echo "activate the development venv by running"
echo "    source .kapidox_venv/bin/activate"
echo "******************************************************************"
