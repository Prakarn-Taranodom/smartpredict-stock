#!/usr/bin/env bash
set -o errexit

apt-get update
apt-get install -y build-essential gcc g++ gfortran libopenblas-dev liblapack-dev

pip install --upgrade pip setuptools wheel
pip install Cython numpy
pip install -r requirements.txt
