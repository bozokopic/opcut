#!/bin/sh

PYTHON=${PYTHON:-python}
RUN_PATH=$(cd $(dirname -- "$0") && pwd)
ROOT_PATH=$RUN_PATH/..

export PYTHONPATH=$ROOT_PATH/src_py
