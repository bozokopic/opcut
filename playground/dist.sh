#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

cd $ROOT_PATH
rm -rf $DIST_PATH
mkdir -p $DIST_PATH


if command -v x86_64-w64-mingw32-gcc >/dev/null; then
    export TARGET_PLATFORM=windows_amd64

    $PYTHON -m doit clean_all
    $PYTHON -m doit dist

    cp $ROOT_PATH/build/py/*.whl $DIST_PATH
    cp $ROOT_PATH/build/dist/*.zip $DIST_PATH
fi


PLATFORMS="linux/amd64
           linux/arm/v7
           linux/arm64/v8"

for PLATFORM in $PLATFORMS; do
    for DOCKERFILE in $PLAYGROUND_PATH/dockerfiles/*; do
        IMAGE=$PLATFORM/$(basename $DOCKERFILE)
        IMAGE_ID=$(podman images -q $IMAGE)

        $PYTHON -m doit clean_all

        podman build --platform $PLATFORM \
                     -f $DOCKERFILE \
                     -t $IMAGE \
                     .
        if [ -n "$IMAGE_ID" -a "$IMAGE_ID" != "$(podman images -q $IMAGE)" ]; then
            podman rmi $IMAGE_ID
        fi
        podman run --rm \
                   --platform $PLATFORM \
                   -v $DIST_PATH:/opcut/dist \
                   -v ~/.cache/pip:/root/.cache/pip \
                   -i $IMAGE /bin/sh - << EOF
set -e
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip hat-json
./playground/requirements.sh > requirements.pip.txt
pip install --upgrade -r requirements.pip.txt
doit clean_all
doit
cp build/py/*.whl dist
EOF

done
done

$PYTHON -m doit clean_all
