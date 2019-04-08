#!/bin/bash

PYTHONPATH=../../src_py python -m opcut calculate \
    --params params.yaml \
    --result result.yaml \
    --output output.pdf \
    $*
