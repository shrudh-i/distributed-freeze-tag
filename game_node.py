# game_node.py
import time
import threading
# import lcm
import pygame
from node import Node

# Import the messages.lcm
from messages import position_t, freeze_t, sync_request_t, sync_confirm_t, game_init_t, gameover_t

class GameNode(Node):

    def __init__(self, width, height, num_not_it):
        '''
        Initialize the GameNode with board dimensions and NotIt agents

        Args:
            width (int): Width of the board
            height (int): Height of the board
            num_not_it (list): List of NotIt agents
        '''
        super().__init__()
        self.width = width
        self.height = height
        self.num_not_it = num_not_it

        # Game state tracking
        self.agents = {} # Map of node_id to position_t
        self.frozen_count = 0
        self.game_active = False
        self.sync_request = set() # To track sync requests from nodes

        # PyGame for visualization
        self.cell_size = 20 # Size of each cell in pixels
        self.screen = None
        self.clock = None
        self.gui_thread = None
        self.gui_running = False

        # To track which NotIt agents are frozen
        self.frozen_agents = set()

    def on_start(self):
        '''
        Initialize LCM subscriptions and start the GUI thread
        '''
        # Subscribe to position updates, sync requests, and game status
        self.subscribe("POSITION", self.handle_position)
        self.subscribe("SYNC_REQUEST", self.handle_sync_request)

        # Initialize and start the GUI thread
        self.gui_thread = threading.Thread(target=self.run_gui)
        self.gui_running = True
        self.gui_thread.start()
    
    def run(self):
        '''
        Main loop for the GameNode
        '''
        try:
            # Wait for the game to be synchronized
            while not self.game_active and self.running:
                time.sleep(0.1)
            
            while self.frozen_count < self.num_not_it and self.running:
                time.sleep(0.1)

            # Send game over message when done
            if self.running:
                game_over_msg = gameover_t()
                self.publish("GAMEOVER", game_over_msg)
                print("GameNode: Game Over! All NotIt agents are frozen.")

            # Wait for a second for other nodes to process the game over message
            time.sleep(1)
        
        except KeyboardInterrupt:
            print("GameNode: Keyboard interrupt. Stopping the game.")
        
        finally:
            self.running = False

    def on_stop(self):
        '''
        Clean up resources when stopping the node
        '''
        # Signal the GUI thread to stop and wait for it to finish
        self.gui_running = False
        if self.gui_thread.is_alive() and self.gui_thread:
            self.gui_thread.join(timeout=1)

        # Close the PyGame window
        if pygame.get_init():
            pygame.quit()

        print("GameNode: Stopped.")

    def handle_position(self, channel, data):
        '''
        Handle incoming position updates from agents

        Args:
            channel (str): LCM channel
            data (bytes): LCM message data
        '''
        msg = position_t.decode(data)
        prev_pose = self.agents.get(msg.node_id)
        self.agents[msg.node_id] = msg

        # Check if this is a new position for a NotIt agent
        if prev_pose is None and msg.is_it == 0:
            print(f"GameNode: NotIt agent {msg.node_id} connected at {msg.x}, {msg.y}")

        if prev_pose is None and msg.is_it == 1:
            print(f"GameNode: It agent connected at {msg.x}, {msg.y}")

        # Check for collision between It and NotIt agents
        if msg.is_it == 1:  # This is an It position update
            it_x, it_y = msg.x, msg.y
            
            # Check all NotIt nodes for collisions with the It node
            for node_id, agent in self.agents.items():
                if (agent.is_it == 0 and  # It's a NotIt node
                    node_id not in self.frozen_agents and  # Not already frozen
                    agent.x == it_x and agent.y == it_y):  # Same position
                    
                    # Freeze the NotIt agent
                    freeze_msg = freeze_t()
                    freeze_msg.node_id = node_id
                    self.publish("FREEZE", freeze_msg)
                    
                    # Mark this agent as frozen
                    self.frozen_agents.add(node_id)
                    self.frozen_count += 1
                    print(f"GameNode: It agent caught NotIt agent {node_id} at ({it_x}, {it_y})! ({self.frozen_count}/{self.num_not_it})")
        
        # Also check for collisions when receiving NotIt position updates
        elif msg.is_it == 0:  # This is a NotIt position update
            # Only check if this NotIt agent isn't already frozen
            if msg.node_id not in self.frozen_agents:
                # Find the It agent position
                it_agent = None
                for agent_id, agent in self.agents.items():
                    if agent.is_it == 1:
                        it_agent = agent
                        break
                
                # If It agent exists and at same position as this NotIt
                if it_agent and it_agent.x == msg.x and it_agent.y == msg.y:
                    # Freeze the NotIt agent
                    freeze_msg = freeze_t()
                    freeze_msg.node_id = msg.node_id
                    self.publish("FREEZE", freeze_msg)
                    
                    # Mark this agent as frozen
                    self.frozen_agents.add(msg.node_id)
                    self.frozen_count += 1
                    print(f"GameNode: It agent caught NotIt agent {msg.node_id} at ({msg.x}, {msg.y})! ({self.frozen_count}/{self.num_not_it})")


    def handle_sync_request(self, channel, data):
        '''
        Handle synchronization requests from agents.
        
        Args:
            channel (str): LCM channel
            data (bytes): LCM message data
        '''

        msg = sync_request_t.decode(data)
        node_type = ["GameNode", "ItNode", "NotItNode"][msg.node_type]

        # Add this node to our set of nodes that are ready
        self.sync_request.add((msg.node_type, msg.node_id))
        print(f"GameNode: Received sync request from {node_type} {msg.node_id}")

        # Check if all (expected) nodes are ready
        expected_count = 1 + self.num_not_it # 1 It node + num_not_it NotIt nodes
        if len(self.sync_request) >= expected_count:
            # ALl nodes are ready, send sync confirmation
            print("GameNode: All nodes are ready. Starting the game!")
            
            confirm_msg = sync_confirm_t()
            confirm_msg.ready = 1
            self.publish("SYNC_CONFIRM", confirm_msg)

            self.game_active = True

    def run_gui(self):
        '''
        RUn the game visualization GUI in a separate thread
        '''
        # Initialize PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.cell_size, self.height * self.cell_size))
        pygame.display.set_caption("Distrubuted Freeze Tag")
        self.clock = pygame.time.Clock()

        # Colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255) 
        GRAY = (200, 200, 200)

        # Main GUI loop
        while self.gui_running:
            # Process PyGame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gui_running = False
                    self.running = False

            # Clear the screen
            self.screen.fill(WHITE)

            # Draw the grid
            for x in range(self.width):
                for y in range(self.height):
                    rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, BLACK, rect, 1)

            # Draw the agents
            for node_id, agent in self.agents.items():
                rect = pygame.Rect(agent.x * self.cell_size, agent.y * self.cell_size, self.cell_size, self.cell_size)

                if agent.is_it == 1:
                    # It agent = RED
                    pygame.draw.rect(self.screen, RED, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 2)  # Border
                
                elif node_id in self.frozen_agents:
                    # Frozen NotIt agent = GRAY
                    pygame.draw.rect(self.screen, GRAY, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 2)
                
                else:
                    # NotIt (active) agent = BLUE
                    pygame.draw.rect(self.screen, BLUE, rect)
                    pygame.draw.rect(self.screen, BLACK, rect, 2)

                # Draw the node ID
                font = pygame.font.Font(None, 24)
                text = font.render(str(node_id), True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

            # Update the display
            pygame.display.flip()
            self.clock.tick(20) # 20 FPS for visualization

        # Clean up PyGame (if its not done already)
        if pygame.get_init():
            pygame.quit()