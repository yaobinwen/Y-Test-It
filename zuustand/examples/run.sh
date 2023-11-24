#!/bin/sh

PY_SCRIPT=$1

: "${PY_SCRIPT:?need to provide the Python script path}"

PYTHONPATH="../src:../../ytestit-common/src:" python3 "$PY_SCRIPT"
