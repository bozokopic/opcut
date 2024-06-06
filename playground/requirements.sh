#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

hat-json-convert $ROOT_PATH/pyproject.toml | \
jq -r '.project | .dependencies[], .["optional-dependencies"][][]'
