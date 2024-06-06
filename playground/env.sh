: ${PLAYGROUND_PATH:?}

PYTHON=${PYTHON:-python3}
ROOT_PATH=$PLAYGROUND_PATH/..
DIST_PATH=$PLAYGROUND_PATH/dist

VERSION=$($PYTHON -m hat.json.convert $ROOT_PATH/pyproject.toml | \
          jq -r .project.version)

export PYTHONPATH=$ROOT_PATH/src_py
