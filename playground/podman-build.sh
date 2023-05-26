#!/bin/sh

. $(dirname -- "$0")/env.sh

cd $ROOT_PATH
exec podman build -t bozokopic/opcut:$(< VERSION) .
