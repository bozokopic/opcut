#!/bin/sh

set -e

RUN_PATH=$(dirname "$(realpath "$0")")
ROOT_PATH=$RUN_PATH/..
. $RUN_PATH/env.sh

BUILD_PATH=$RUN_PATH/build

rm -rf $BUILD_PATH
mkdir -p $BUILD_PATH

cd $ROOT_PATH

$PYTHON -m doit clean_all
$PYTHON -m doit wheel
cp $ROOT_PATH/build/py/*.whl $BUILD_PATH

if command -v x86_64-w64-mingw32-gcc > /dev/null; then
    export TARGET_PLATFORM=windows_amd64
    $PYTHON -m doit clean_all
    $PYTHON -m doit dist
    cp $ROOT_PATH/build/py/*.whl $BUILD_PATH
    cp $ROOT_PATH/build/dist/*.zip $BUILD_PATH
fi
