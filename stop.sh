#!/bin/bash

PYRAMID_PORT=8080
LIVERELOAD_PORT=35729

PYRAMID_PID=`lsof -i:$PYRAMID_PORT -t`
LIVERELOAD_PID=`lsof -i:$LIVERELOAD_PORT -t`

if [ ! -z "$PYRAMID_PID" ]; then
  wait `kill -9 $PYRAMID_PID`
fi

if [ ! -z "$LIVERELOAD_PID" ]; then
  wait `kill -9 $LIVERELOAD_PID`
fi

wait `find . -name "*.pyc" -type f -delete`

exit 0
