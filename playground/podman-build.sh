#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

cd $ROOT_PATH

PLATFORM=linux/amd64

podman build --platform $PLATFORM \
             -f Dockerfile \
             -t bozokopic/opcut:$VERSION \
             .

podman build --platform $PLATFORM \
             -f Dockerfile.alpine \
             -t bozokopic/opcut:alpine-$VERSION \
             .
