#!/bin/bash

# First allow X connections from local containers
xhost +local:docker

# Then run with access to your display
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  freeze-tag --width 20 --height 15 --num-not-it 2 --positions 3 5 10 12 0 0