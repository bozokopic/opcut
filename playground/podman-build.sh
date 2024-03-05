#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

cd $ROOT_PATH
exec podman build -t bozokopic/opcut:$VERSION .
