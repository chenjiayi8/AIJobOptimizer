#!/bin/bash

# Create a new virtual environment
virtualenv --python=python3.10 $HOME/env
source $HOME/env/bin/activate

# Install dependencies from requirements.txt
pip install -r ./requirements.txt
