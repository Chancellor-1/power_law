@echo off
py -m venv .venv
call .venv\Scripts\activate
py -m pip install --upgrade pip setuptools
pip install .
call deactivate
