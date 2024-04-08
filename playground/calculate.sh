#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

exec $PYTHON -m opcut calculate \
    --method forward_greedy \
    --output $PLAYGROUND_PATH/result.json \
    $PLAYGROUND_PATH/params.json
