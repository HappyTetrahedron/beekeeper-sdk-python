#!/bin/bash
cd beekeeper-sdk
python setup.py sdist bdist_wheel
cd ..
cd chatbot-sdk
python setup.py sdist bdist_wheel
cd ..
