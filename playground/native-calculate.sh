#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $ROOT_PATH/src_py/opcut/bin/linux-opcut-calculate \
    --method greedy \
    --output result.json \
    params.json
