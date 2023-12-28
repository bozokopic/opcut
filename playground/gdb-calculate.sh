#!/bin/sh

set -e

RUN_PATH=$(dirname "$(realpath "$0")")
ROOT_PATH=$RUN_PATH/..
. $RUN_PATH/env.sh

PYTHON_BIN="$($PYTHON -c "import sys; print(sys.executable)")"


cd $ROOT_PATH
doit clean_all
doit json_schema_repo libopcut

cd $RUN_PATH
exec gdb --directory $ROOT_PATH \
         --command $RUN_PATH/gdb-calculate.gdb \
         --args $PYTHON_BIN -m opcut calculate \
                            --method forward_greedy_native \
                            --output $RUN_PATH/result.json \
                            $RUN_PATH/params.json
