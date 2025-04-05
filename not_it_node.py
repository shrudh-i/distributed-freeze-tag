# not_it_node.py
import time
import random
# import lcm
from node import Node

# Import the messages.lcm
from messages import position_t, freeze_t, sync_request_t, sync_confirm_t

class NotItNode(Node):
    def __init__(self, node_id, start_x, start_y, width, height):
        '''
        Initialize a NotItNode
        
        Args:
            node_id (int): Unique identifier for the NotItNode
            start_x (int): Starting x-coordinate of the NotItNode
            start_y (int): Starting y-coordinate of the NotItNode
            width (int): Width of the board
            height (int): Height of the board
        '''
        super().__init__()
        self.node_id = node_id
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height
        self.frozen = False
        self.game_active = False

    def on_start(self):
        '''
        Initialize LCM subscriptions and send initial position
        '''
        # Subscribe to synchronization confirmation and freeze events
        self.subscribe("SYNC_CONFIRM", self.handle_sync_confirm)
        self.subscribe("FREEZE", self.handle_freeze)
        self.subscribe("GAME_OVER", self.handle_game_over)

        # Send sync request to the GameNode
        sync_request = sync_request_t()
        sync_request.node_type = 2 # 2 for NotItNode
        sync_request.node_id = self.node_id
        self.publish("SYNC_REQUEST", sync_request)

        # Send initial position
        self.publish_position()
        print(f"NotItNode {self.node_id}: Started at position ({self.x}, {self.y})")

    def run(self):
        '''
        Main loop for the NotItNode
        '''
        try:
            # Wait for synchronization confirmation
            while not self.game_active and self.running:
                time.sleep(0.1)

            print(f"NotItNode {self.node_id}: Game active, starting movement")
            

            while not self.frozen and self.running:
                # NotItNode moves randomly
                self.move_randomly()
                self.publish_position()

                # Wait for a second before next move
                time.sleep(1)
            
            # If frozen, stay in place but keep publishing position
            while self.frozen and self.running:
                self.publish_position()
                time.sleep(1)

        except KeyboardInterrupt:
            print(f"NotItNode {self.node_id}: Interrupted by user")
            # self.running = False
        
    def on_stop(self):
        '''
        Stop the NotItNode: Clean up resources
        '''
        print(f"NotItNode {self.node_id}: Stopping")
        # TODO: check if we need self.running here
        # self.running = False

    def move_randomly(self, attempts=0, max_attempts=10):
        '''
        Move to a random adjacent position within the board
        '''
        # Stop if we've tried too many times
        if attempts >= max_attempts:
            print(f"NotItNode {self.node_id}: Couldn't find a valid move after {max_attempts} attempts, staying at ({self.x}, {self.y})")
            return

        # Possible moves: up, down, left, right (no diagonal moves)
        moves = [
                    (0, 1),  #DOWN
                    (0, -1), #UP 
                    (1, 0),  #LEFT
                    (-1, 0)  #RIGHT
                ]
        
        # Randomly select a move
        dx, dy = random.choice(moves)

        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy

        # Make sure the new position is within the board boundaries
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.x = new_x
            self.y = new_y
            print(f"NotItNode {self.node_id}: Moved to position ({self.x}, {self.y})")

        else:
            # If the move is out of bounds, try again with an attempt counter
            self.move_randomly(attempts + 1, max_attempts)

    def publish_position(self):
        '''
        Publish the current position to the POSITION channel
        '''
        pose = position_t()
        pose.node_id = self.node_id
        pose.x = self.x
        pose.y = self.y
        pose.is_it = 0 #NotItNode
        self.publish("POSITION", pose)

    def handle_sync_confirm(self, channel, data):
        '''
        Handle synchronization confirmation from the GameNode
        '''
        msg = sync_confirm_t.decode(data)
        if msg.ready == 1:
            self.game_active = True
            print(f"NotItNode {self.node_id}: Received synchronization confirmation")

    def handle_freeze(self, channel, data):
        '''
        Handle freeze message from the GameNode

        Args:
            channel (str): LCM channel
            data (bytes): LCM message data
        '''
        msg = freeze_t.decode(data)
        if msg.node_id == self.node_id and not self.frozen:
            self.frozen = True
            print(f"NotItNode {self.node_id}: I've been frozen!")
            # Immediately publish updated position to confirm frozen state
            self.publish_position()

    def handle_game_over(self, channel, data):
        '''
        Handle game over message from the GameNode
        '''
        print(f"NotItNode {self.node_id}: Game over!")
        self.running = False
        self.stop()