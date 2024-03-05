: ${PLAYGROUND_PATH:?}

PYTHON=${PYTHON:-python3}
ROOT_PATH=$PLAYGROUND_PATH/..
VERSION=$($PYTHON -m hat.json.convert $ROOT_PATH/pyproject.toml | \
          jq -r .project.version)

export PYTHONPATH=$ROOT_PATH/src_py
