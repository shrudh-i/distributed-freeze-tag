##############################################
##      Bash script v1: Default inputs      ##
##############################################

# #!/bin/bash

# # First allow X connections from local containers
# xhost +local:docker

# # Then run with access to your display
# docker run -it --rm \
#   -e DISPLAY=$DISPLAY \
#   -v /tmp/.X11-unix:/tmp/.X11-unix \
#   freeze-tag --width 20 --height 15 --num-not-it 2 --positions 3 5 10 12 0 0


##############################################
##   Bash script v2: User can give inputs   ##
##############################################

#!/bin/bash

# Allow X connections from local containers
xhost +local:docker

# Default values provided from challenge (in case user doesn't pass them)
WIDTH=20
HEIGHT=15
NUM_NOT_IT=2
POSITIONS=(3 5 10 12 0 0)

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --width)
      WIDTH="$2"
      shift 2
      ;;
    --height)
      HEIGHT="$2"
      shift 2
      ;;
    --num-not-it)
      NUM_NOT_IT="$2"
      shift 2
      ;;
    --positions)
      POSITIONS=()
      shift
      while [[ $# -gt 0 && ! $1 =~ ^-- ]]; do
        POSITIONS+=("$1")
        shift
      done
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Print the parsed values
echo "WIDTH: $WIDTH"
echo "HEIGHT: $HEIGHT"
echo "NUM_NOT_IT: $NUM_NOT_IT"
echo "POSITIONS: ${POSITIONS[@]}"

# Then run with access to your display
sudo docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  freeze-tag --width $WIDTH --height $HEIGHT --num-not-it $NUM_NOT_IT --positions ${POSITIONS[@]}