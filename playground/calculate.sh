#!/bin/sh

set -e

RUN_PATH=$(dirname "$(realpath "$0")")
ROOT_PATH=$RUN_PATH/..
. $RUN_PATH/env.sh

exec $PYTHON -m opcut calculate \
    --method forward_greedy_native \
    --output $RUN_PATH/result.json \
    $RUN_PATH/params.json
