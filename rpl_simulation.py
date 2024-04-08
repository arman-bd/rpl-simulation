import simpy
import random

# Constants for the simulation
BROADCAST_TIME = 1  # Time it takes to simulate broadcasting a message across a network.
DISCOVERY_TIME = 5  # Time after which the node starts the neighbor discovery process.
DIO_INTERVAL = 10   # Time interval at which DIO messages are sent.

class Node:
    def __init__(self, env, node_id):
        """
        Initialize a new node within the network simulation.
        
        Args:
        - env: The SimPy environment in which the node operates.
        - node_id: A unique identifier for the node.
        """
        self.env = env  # Simulation environment
        self.node_id = node_id  # Unique ID for the node
        self.neighbors = []  # List to keep track of neighboring nodes
        self.msg_queue = simpy.Store(env)  # Queue to store incoming messages
        self.rank = None  # Node's rank in the DODAG, root node starts with rank 0
        
    def add_neighbor(self, neighbor_node):
        """
        Adds a neighboring node to the node's list of neighbors. This is a crucial
        part of setting up the network topology.
        
        Args:
        - neighbor_node: The node object to be added as a neighbor.
        """
        self.neighbors.append(neighbor_node)
    
    def send_message(self, message, delay=0):
        """
        Simulates sending a message to all neighboring nodes after a specified delay.
        
        Args:
        - message: The message to be sent.
        - delay: Time to wait before sending the message.
        """
        yield self.env.timeout(delay)  # Simulate delay
        for neighbor in self.neighbors:
            # Process of sending the message to each neighbor
            print(f"{self.env.now}: Node {self.node_id} sends message to Node {neighbor.node_id}")
            self.env.process(neighbor.receive_message(message))
    
    def receive_message(self, message):
        """
        Receives an incoming message and places it in the node's message queue.
        
        Args:
        - message: The incoming message to be processed.
        """
        yield self.msg_queue.put(message)
    
    def run(self):
        """
        Defines the node's behavior in the simulation, such as neighbor discovery
        and handling DIO messages.
        """
        # Begin neighbor discovery after some time has passed.
        yield self.env.timeout(DISCOVERY_TIME)
        self.discover_neighbors()

        # Periodically send DIO messages if the node is part of the DODAG.
        while True:
            if self.rank is not None:  # Nodes must have a rank to send DIO messages
                yield self.env.process(self.send_dio())
            yield self.env.timeout(DIO_INTERVAL)  # Wait for the next DIO interval

    def discover_neighbors(self):
        """
        Simulates the process of neighbor discovery for the node. This is a placeholder
        and should be replaced with an actual discovery process.
        """
        print(f"{self.env.now}: Node {self.node_id} starts neighbor discovery")

    def send_dio(self):
        """
        Simulates sending a DIO message to inform neighbors of the node's presence
        in the DODAG and its rank.
        """
        dio_message = f"DIO from Node {self.node_id}"
        yield self.env.process(self.send_message(dio_message))

    def process_dio(self, message):
        """
        Processes a received DIO message, setting the node's rank if it doesn't have one.
        This simulates the node joining the DODAG. In an actual RPL implementation, the
        node would select its parent based on the DIO information and compute its rank accordingly.
        """
        if self.rank is None:
            # Assign a random rank as a placeholder for actual rank determination logic.
            self.rank = random.randint(1, 100)  # Random rank for demonstration purposes
            print(f"{self.env.now}: Node {self.node_id} sets rank to {self.rank}")

class Network:
    def __init__(self, env):
        """
        Initialize a new network for the simulation.
        
        Args:
        - env: The SimPy environment in which the network operates.
        """
        self.env = env
        self.nodes = {}  # Dictionary to store and access nodes by their ID
    
    def add_node(self, node_id):
        """
        Adds a new node to the network with the given ID.
        
        Args:
        - node_id: The identifier for the new node.
        
        Returns:
        The newly created node object.
        """
        node = Node(self.env, node_id)
        self.nodes[node_id] = node
        return node
    
    def run(self):
        """
        Starts the simulation of the network, initiating the run process for each node.
        """
        for node in self.nodes.values():
            yield self.env.process(node.run())


# Set up the SimPy environment
env = simpy.Environment()

# Create a network instance within the environment
network = Network(env)

# Add nodes to the network
node_a = network.add_node('A')  # This could be the designated root node.
node_b = network.add_node('B')
node_c = network.add_node('C')

# Define neighbors (for simplicity, in a linear topology)
node_a.add_neighbor(node_b)
node_b.add_neighbor(node_a)
node_b.add_neighbor(node_c)
node_c.add_neighbor(node_b)

# Set the rank of the root node to 0 to start the DODAG
node_a.rank = 0

# Start the network simulation, which will cause nodes to run their behavior routines
env.process(network.run())

# Execute the simulation for a specified amount of time
env.run(until=50)
