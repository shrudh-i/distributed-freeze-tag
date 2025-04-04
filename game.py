# game.py
import multiprocessing

from node import Node

def main():
    """
    Main function to parse arguments and launch the required nodes.
    """

    # Example of launching a Node and then killing it.
    node = Node()
    node_process = multiprocessing.Process(target=node.launch_node, name="Node")
    node_process.join()
    

if __name__ == "__main__":
    main()
