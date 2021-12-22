#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $ROOT_PATH/build/c/opcut-calculate \
    --method greedy \
    --output result.json \
    params.json
