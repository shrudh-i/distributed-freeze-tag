# it_node.py
import time
# import lcm
from node import Node

# Import the messages.lcm
from messages import position_t, sync_request_t, sync_confirm_t

class ItNode(Node):
    def __init__(self, start_x, start_y, width, height):
        '''
        Initialize the ItNode with starting position and board dimensions

        Args:
            start_x (int): Starting x-coordinate of the ItNode
            start_y (int): Starting y-coordinate of the ItNode
            width (int): Width of the board
            height (int): Height of the board
        '''
        super().__init__()
        self.node_id = 0 # ID for the ItNode should be 0
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height
        self.game_active = False

        # Game state tracking
        self.not_it_nodes = {}
        self.frozen_nodes = set()
    
    def on_start(self):
        '''
        Initialize LCM subscriptions & send initial position
        '''
        # Subscribe to position updates and sync requests
        self.subscribe("SYNC_CONFIRM", self.handle_sync_confirm)
        self.subscribe("POSITION", self.handle_position)
        self.subscribe("GAME_OVER", self.handle_game_over)

        # Send sync request to the GameNode
        sync_request = sync_request_t()
        sync_request.node_type = 0 # 1 for ItNode
        sync_request.node_id = self.node_id
        self.publish("SYNC_REQUEST", sync_request)

        # Send initial position
        self.publish_position()
        print(f"ItNode: Started at position ({self.x}, {self.y})")
    
    def run(self):
        '''
        Main loop for the ItNode
        '''
        try:
            # Wait for synchronization confirmation
            while not self.game_active and self.running:
                time.sleep(0.1)
            
            print("ItNode: Game active, starting movement")

            # Main loop for the ItNode
            while self.running:
                # Chase closes unfrozen NotIt agents
                self.chase_closest_not_it()
                self.publish_position()

                # Wait for a short period before next move
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("ItNode: Interrupted by user")

    def on_stop(self):
        '''
        Stop the ItNode
        '''
        # TODO: check if we need self.running here
        # self.running = False
        print("ItNode: Stopped")

    def chase_closest_not_it(self):
        '''
        Chase the closest unfrozen NotIt agent
        '''
        closest_node_id = None
        closest_distance = float('inf')

        # Find the closest unfrozen NotIt node
        for node_id, (x, y) in self.not_it_nodes.items():
            if node_id not in self.frozen_nodes:
                # Calculate Manhattan distance
                distance = abs(self.x - x) + abs(self.y - y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_node_id = node_id

        # If no unfrozen nodes or all nodes are frozen, do nothing
        if closest_node_id is None:
            return
        
        # Get position of closest NotIt
        target_x, target_y = self.not_it_nodes[closest_node_id]
        
        # Determine best move direction (prioritize larger axis difference)
        dx = target_x - self.x
        dy = target_y - self.y
        
        if abs(dx) >= abs(dy):
            # Move horizontally first
            if dx > 0:
                self.x = min(self.x + 1, self.width - 1)
            elif dx < 0:
                self.x = max(self.x - 1, 0)
        else:
            # Move vertically first
            if dy > 0:
                self.y = min(self.y + 1, self.height - 1)
            elif dy < 0:
                self.y = max(self.y - 1, 0)
                
        print(f"ItNode: Moved to ({self.x}, {self.y}), chasing NotIt node {closest_node_id}")
    
    def publish_position(self):
        '''
        Publish the current position of the ItNode to the POSITION channel
        '''
        pose = position_t()
        pose.node_id = self.node_id
        pose.x = self.x
        pose.y = self.y
        pose.is_it = 1

        self.publish("POSITION", pose)

    def handle_sync_confirm(self, channel, data):
        '''
        Handle synchronization confirmation from the GameNode

        Args:
            channel (str): LCM channel
            data (bytes): LCM message data
        '''
        msg = sync_confirm_t.decode(data)
        if msg.ready == 1 and msg.node_id == self.node_id:
            self.game_active = True
            print("ItNode: Received sync confirmation, game is active")

    def handle_position(self, channel, data):
        '''
        Handle position updates from NotIt nodes

        Args:
            channel (str): LCM channel
            data (bytes): LCM message data
        '''
        msg = position_t.decode(data)

        if msg.is_it == 0:
            self.not_it_nodes[msg.node_id] = (msg.x, msg.y)
            # print(f"ItNode: Received position update from NotIt node {msg.node_id} at ({msg.x}, {msg.y})")

            # Check if the NotIt node pose is same as It node pose
            if self.x == msg.x and self.y == msg.y:
                print(f"ItNode: Caught NotIt node {msg.node_id} at ({msg.x}, {msg.y})!")
                self.frozen_nodes.add(msg.node_id)

    def handle_game_over(self, channel, data):
        '''
        Handle game over message from GameNode

        Args:
            channel (str): LCM channel
            data (bytes): LCM message data
        '''
        print("ItNode: Game over!")
        self.running = False
        # sys.exit(0)