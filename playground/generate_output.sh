#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $PYTHON -m opcut generate_output \
    --output-type pdf \
    --result $RUN_PATH/result.json \
    --output $RUN_PATH/output.pdf \
    "$@"
