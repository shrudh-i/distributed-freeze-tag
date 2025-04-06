# Freeze Tag Game - Technical Deep Dive

This document provides a detailed explanation of the technical implementation of the Distributed Freeze Tag Game!

## ItNode Chase Algorithm

The ItNode employs the following chasing strategy to efficiently catch the nearest NotIt nodes:

1. **Target Selection**:
   - Calculates Manhattan distance (|x₁-x₂| + |y₁-y₂|) to all unfrozen NotIt nodes
      - I chose this because the ItNode cannot move diagonally, making this the ideal heuristic to employ
      - This allows for the ItNode to prioritize the closest unfrozen NotIt node to catch

2. **Predictive Movement**:
   - For targets more than 2 units away, I implemented a simple predictive algorithm
      - Instead of directly chasing the current position, it attempts to intercept the NotIt node
      - By calculating an intercept point slightly ahead of the NotIt's current position in the same general direction

3. **Direction Priority**:
   - Prioritizes movement along the axis with the larger difference first
      - If horizontal distance is greater or equal to vertical distance, moves horizontally first
      - Otherwise, moves vertically first
   - This creates more direct paths to the target

4. **Boundary Awareness**:
   - Ensures all calculated moves remain within board boundaries
   - Prevents the ItNode from moving off the game board

5. **Move Frequency**:
   - ItNode moves every 0.5 seconds, while NotItNodes move every 1 second
   - This speed advantage helps the ItNode catch the NotItNodes more effectively

## GameNode Signal Management

The GameNode coordinates the entire game, through the following signal management:

1. **Synchronization Protocol**:
   - Collects `SYNC_REQUEST` messages from all nodes
   - Maintains a set of nodes that are ready to begin
   - Once all expected nodes have checked in, broadcasts a `SYNC_CONFIRM` signal
   - This ensures all nodes start moving simultaneously for fair gameplay

2. **Position Tracking**:
   - Maintains a dictionary mapping node IDs to their current positions
   - Updates positions in real-time as `POSITION` messages are received
   - Uses this data to detect collisions between It and NotIt nodes

3. **Collision Detection**:
   - Implements dual-direction collision detection:
     - When It node reports position, checks for collisions with all NotIt nodes
     - When NotIt nodes report positions, checks for collision with the It node
   - This redundancy ensures no collisions are missed due to network delays

4. **Freeze Management**:
   - When a collision is detected, sends a `FREEZE` message to the caught NotIt node
   - Tracks which NotIt nodes are frozen using a set data structure
   - Increments frozen counter to determine game completion

5. **Game State Visualization**:
   - Runs PyGame visualization in a separate thread to prevent blocking
   - Updates the display at 20 FPS for smooth visualization
   - Color-codes agents: Red (It), Blue (active NotIt), Gray (frozen NotIt)

6. **Game Termination**:
   - Monitors frozen count against total NotIt nodes
   - When all NotIt nodes are frozen, broadcasts `GAMEOVER` message
   - Coordinates clean shutdown of all nodes

## NotItNode Movement and Behavior

The NotItNode implements the following mechanics:

1. **Random Movement Algorithm**:
   - Moves in one of four cardinal directions: up, down, left, or right
   - By leveraging `random.choice()` to select a direction uniformly
   - No diagonal movements are allowed

2. **Boundary Handling**:
   - Uses a recursive approach with attempt counting to find valid moves
   - If a randomly chosen move would go out of bounds, tries again with a different random direction
   - I implemented a maximum attempt limit (10) to prevent infinite recursion
   - If no valid move is found after maximum attempts, stays in place

3. **Freeze Response**:
   - Upon receiving a `FREEZE` message matching its node_id, sets frozen state to True
   - Immediately publishes its position to confirm the frozen state
   - Stops moving but continues to publish its position every second

4. **Signal Handling**:
   - Listens for:
     - `SYNC_CONFIRM`: To start movement
     - `FREEZE`: To stop movement when caught
     - `GAME_OVER`: To terminate cleanly

5. **Resource Management**:
   - I implemented proper cleanup in `on_stop()` method
   - This ensures all resources are released when the node terminates

## LCM Communication Architecture

The system uses a publish-subscribe pattern via LCM:

1. All nodes inherit from a base `Node` class that handles:
   - LCM initialization
   - Message subscription
   - Message publishing
   - Thread management for asynchronous message handling

2. Communication channels include:
   - `POSITION`: For position updates from all agents
   - `SYNC_REQUEST`: For synchronization requests
   - `SYNC_CONFIRM`: For synchronization confirmation
   - `FREEZE`: For freeze commands
   - `GAMEOVER`: For game termination signals

This distributed architecture ensures nodes operate independently while maintaining game coherence through message passing.
