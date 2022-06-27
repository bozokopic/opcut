#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $PYTHON -m opcut generate \
    < $RUN_PATH/result.json \
    > $RUN_PATH/output.pdf \
