# Distributed Freeze Tag Game

This project implements a distributed real-time Freeze Tag game using multiple agents that communicate over a network using LCM (Lightweight Communications and Marshalling).

## Game Rules
- One agent is designated as "It" and the rest are "NotIt" agents
- The "It" agent's goal is to chase and freeze all "NotIt" agents
- The game continues until all "NotIt" agents have been frozen

## Dependencies
- Python 3.9+
- LCM (Lightweight Communications and Marshalling)
- PyGame for visualization

## Running with Docker

### Prerequisites
- Docker installed on your system
   - You can install it through: `sudo apt install docker.io`
   - Note: Ensure you do a `pip install --upgrade pip` once installed

### Building the Docker Image
```bash
sudo docker build -t freeze-tag .
```

### Running the Game
There is an executable bash script `run_freeze_tag.sh` designed to take in parameters to start the game in the Docker container!
```bash
./run_freeze_tag.sh --width 20 --height 15 --num-not-it 2 --positions 3 5 10 12 0 0
```

**Parameters:**
- `--width`: Width of the game board
- `--height`: Height of the game board
- `--num-not-it`: Number of "NotIt" agents
- `--positions`: Positions of all agents (format: x1 y1 x2 y2 ... x_it y_it)

**Note:<br>**
If no parameters are passed in, it defaults to the example command given in the challenge.
- Creates a 20x15 board
- Sets up 2 "NotIt" agents at positions (3,5) and (10,12)
- Places the "It" agent at position (0,0)

## Running without Docker

### Installation
1. Install LCM:
```bash
sudo apt install liblcm-dev
```

2. Generate LCM Python bindings:
```bash
lcm-gen -p messages.lcm
```  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Ensure you're in the directory where `messages.lcm` is in before running this. This will generate the source code required to establish communication when the game is running.

3. Install Python dependencies:
```bash
pip install pygame lcm
```

### Running the Game
```bash
python game.py --width 20 --height 15 --num-not-it 2 3 5 10 12 0 0
```

## Implementation Details

### Components
1. **GameNode**
   - Manages the game state
   - Tracks positions of all agents
   - Detects collisions and sends freeze messages
   - Visualizes the game using PyGame

2. **ItNode**
   - Chases "NotIt" agents using a simple heuristic
   - Listens for position updates from all agents
   - Strategically moves to catch "NotIt" agents

3. **NotItNode**
   - Moves randomly within board boundaries
   - Stops moving when frozen
   - Publishes position updates

### Message Types
- `gameover_t`: Signals the end of the game
- `position_t`: Used by both It and NotIt nodes to publish their positions
- `freeze_t`: Sent to the NotIt node when it's caught
- `sync_request_t`: Used to synchronize before the game starts
- `sync_confirm_t`: Confirms that all nodes are ready to start
- `game_init_t`: Passes game parameters to all nodes

## Technical Documentation

For detailed implementation information about the algorithms, communication architecture, and node behaviors, please see the [technical deep dive](technical-deep-dive.md).