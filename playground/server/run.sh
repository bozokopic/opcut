#!/bin/bash

export PYTHONPATH=../../src_py
python -m opcut.main server --ui-path ../../build/jsopcut
