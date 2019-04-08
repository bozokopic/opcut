#!/bin/bash

PYTHONPATH=../../src_py python -m opcut server \
    --ui-path ../../build/jsopcut \
    $*
