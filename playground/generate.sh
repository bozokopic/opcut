#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

exec $PYTHON -m opcut generate \
    <$PLAYGROUND_PATH/result.json \
    >$PLAYGROUND_PATH/output.pdf \
