: ${ROOT_PATH:?}

PYTHON=${PYTHON:-python3}
VERSION=$($PYTHON -m hat.json.convert $ROOT_PATH/pyproject.toml | \
          jq -r .project.version)

export PYTHONPATH=$ROOT_PATH/src_py
