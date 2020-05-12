#!/bin/bash

# Requires python setuptools and wheel to be installed

cd beekeeper-sdk
python setup.py sdist bdist_wheel
cd ..
cd chatbot-sdk
python setup.py sdist bdist_wheel
cd ..
