#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

PYTHON_BIN="$($PYTHON -c "import sys; print(sys.executable)")"


cd $ROOT_PATH
doit clean_all
doit json_schema_repo libopcut

cd $PLAYGROUND_PATH
exec gdb --directory $ROOT_PATH \
         --command $PLAYGROUND_PATH/gdb-calculate.gdb \
         --args $PYTHON_BIN -m opcut calculate \
                            --method forward_greedy_native \
                            --output $PLAYGROUND_PATH/result.json \
                            $PLAYGROUND_PATH/params.json
