#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $PYTHON -m opcut calculate \
    --method forward_greedy \
    --output $RUN_PATH/result.json \
    $RUN_PATH/params.json
