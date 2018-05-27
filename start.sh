#!/bin/bash

wait `./stop.sh`

venv/bin/pserve development.ini --reload & gulp open
