#!/bin/bash

set -e

if [[ $TRAVIS_OS_NAME == "osx" ]]; then
    . ./venv/bin/activate
fi

nosetests -sv
