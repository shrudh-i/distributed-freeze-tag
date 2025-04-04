# distributed-freeze-tag

## Dependencies within the Docker container:
### 1. LCM installation:
``` 
sudo apt install liblcm-dev
```

## Approach:

To solve this challenge, I took the following approach:
### 1. Completing the messages.lcm
* From analysing the requirements of the game, I wanted to first expand the messages.lcm file with additional message types for the game's communication
* Essentially, this establishes the communication protocols before we begin deving game.py 

### 2. Structuring version-1 of `game.py`
* After defining all the message types, it made sense to structure out what I would like each node to take in and how those processes would look like
* In `game.py`, I implemented functionalities to parse the arguments (defined in the question), and start different processes for each node
* I defined the game's termination condition - essentially, when the GameNode stops - and included functionalities to kill all processes when the game is over

### 3. Defining the Nodes: GameNode, NotItNode, ItNode:
#### 3.1. GameNode implemetation
* 


## Message types I've created for the game:
* `gameover_t`: Signals the end of the game
* `position_t`: Used by both It and NotIt nodes to publish their positions
* `freeze_t`: Send to the NotIt node when its caught
* `sync_request_t`: Used to sync before the game starts
* `sync_confirm_t`: Confirms that all nodes are ready to start
* `game_init_t`: Passes game params to all nodes