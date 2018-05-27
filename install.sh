#!/bin/bash

if [ -d "venv" ]; then
  echo "Virtual environment exists"
else
  echo "Creating virtual environment ..."
  virtualenv --python=python2.7 venv
  echo "Virtual environment created"
fi

echo "Updating virtual environment ..."
venv/bin/pip install --default-timeout=60 -e .
venv/bin/pip install --default-timeout=60 -r requirements.txt
echo "Virtual environment updated"

echo "Updating Node dependencies ..."
npm i
echo "Node dependencies updated"

echo "Updating R dependencies ..."
# sudo su - -c "R -e \"install.packages('ggplot2')\""
R -e "install.packages('ggplot2')"
echo "R dependencies updated"
