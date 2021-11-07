#!/bin/sh

. $(dirname -- "$0")/env.sh

cd $ROOT_PATH
exec $PYTHON -m doit
