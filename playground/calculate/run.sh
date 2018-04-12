#!/bin/bash

export PYTHONPATH=../../src_py
python -m opcut.main calculate --params params.yaml --result result.yaml --output-pdf output.pdf $*
