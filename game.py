# game.py
import multiprocessing
import argparse
import signal
import time
import lcm
import sys 

from game_node import GameNode
from it_node import ItNode
from not_it_node import NotItNode


def parse_arguments():
    parser = argparse.ArgumentParser(description='Distributed Freeze Tag Game')
    parser.add_argument('--width', type=int, required=True, help='Width of the game board')
    parser.add_argument('--height', type=int, required=True, help='Height of the game board')
    parser.add_argument('--num-not-it', type=int, required=True, help='Number of NotIt agents')
    parser.add_argument('--positions', type=int, nargs='+', required=True, 
                        help='Positions for all agents: [not_it_1_x not_it_1_y ... not_it_n_x not_it_n_y it_x it_y]')
    
    args = parser.parse_args()
    
    # Validate number of positions matches the number of agents
    expected_positions = 2 * (args.num_not_it + 1)  # NotIt agents + It agent, each with x and y
    if len(args.positions) != expected_positions:
        parser.error(f"Expected {expected_positions} position values but got {len(args.positions)}")
    
    return args

def main():
    """
    Main function to parse arguments and launch the required nodes.
    """

    # # Example of launching a Node and then killing it.
    # node = Node()
    # node_process = multiprocessing.Process(target=node.launch_node, name="Node")
    # node_process.join()
    
    args = parse_arguments()

    # Extract positions 
    not_it_positions = []
    for i in range(args.num_not_it):
        # Append the (x,y) pairs for NotIt agents
        not_it_positions.append((args.positions[2*i], args.positions[2*i + 1]))

    # Set the (x,y) pair for the It agent
    it_position = (args.positions[-2], args.positions[-1])

    # Create processes list to tack
    processes = []

    try:
        # Start the game node first 
        game_node = GameNode(args.width, args.height, args.num_not_it)
        game_process = multiprocessing.Process(target=game_node.launch_node, name="GameNode")
        game_process.start()
        processes.append(game_process)

        # Allow the game node to initialize
        time.sleep(0.5)

        # Start the It node
        it_node = ItNode(it_position[0], it_position[1], args.width, args.height)
        it_process = multiprocessing.Process(target=it_node.launch_node, name="ItNode")
        it_process.start()
        processes.append(it_process)

        # Start the NotIt nodes
        for i in range(args.num_not_it):
            not_it_node = NotItNode(i+1, not_it_positions[i][0], not_it_positions[i][1], args.width, args.height)
            not_it_process = multiprocessing.Process(target=not_it_node.launch_node, name=f"NotItNode_{i+1}")
            not_it_process.start()
            processes.append(not_it_process)

        # Wait for the game node to finish (it will, once the game is over)
        game_process.join()

    except KeyboardInterrupt:
        print("Game interrupted. Terminating all nodes...")

    finally:
        # Clean up all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=1.0)

                # Force kill the process if it doesn't terminate
                if process.is_alive():
                    print(f"Process {process.name} did not terminate. Killing it.")
                    process.kill()
        
        print("All processes terminated.")

if __name__ == "__main__":
    main()
