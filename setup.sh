#!/bin/bash
python3 -m venv .venv
if [ $? -eq 0 ]
then
  echo "Successfully created virtual environment venv"
else
  echo "Failed to create virtual environment venv" >&2
  exit 1
fi
source .venv/bin/activate; \
python3 -m pip install --upgrade pip setuptools; \
pip3 install .
