#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

for i in $(find $ROOT_PATH/src_py -name '*.so'); do
    objdump -T $i | grep GLIBC
done
