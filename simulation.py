import os
import builtins
import random
import simpy
import matplotlib.pyplot as plt

# Delete simulation.txt file if exists
if os.path.exists('output.txt'):
    os.remove('output.txt')

# Redirect print to a File
def print(*args, **kwargs):
    with open('output.txt', 'a') as f:
        builtins.print(*args, **kwargs, file=f)
    builtins.print(*args, **kwargs)

# Simulation parameters
RANDOM_SEED = 442 # Seed for random number generation
NUM_NODES = 50  # Total number of nodes
AREA_WIDTH = 125  # Meters
AREA_HEIGHT = 125  # Meters
MINIMUM_DISTANCE = 5  # Minimum distance between nodes
CONNECTION_RANGE = 25  # Maximum range for connecting to other nodes
DIO_INTERVAL = 5  # Time between DIO messages in seconds
NODE_CREATION_INTERVAL = 1  # Delay in seconds between node creations

random.seed(RANDOM_SEED + random.randint(0, 1000))

class Node:
    def __init__(self, env, node_id, position, all_nodes):
        self.env = env
        self.node_id = node_id
        self.position = position
        self.all_nodes = all_nodes
        self.neighbors = []
        self.parent = None
        # Create a unique prefix for the node
        self.prefix = f'2001:db8::{int(node_id[4:]):02x}'
        # Trickle parameters
        self.Imin = 1
        self.Imax = 10
        self.I = self.Imin
        self.t = random.uniform(self.Imin, self.I)

    def _discover_neighbors(self):
        print(f'{self.env.now:.2f} {self.node_id} created at {self.position} and starting neighbor discovery')
        for node in self.all_nodes:
            if node != self:
                distance = self.calculate_distance(node.position)
                if distance <= CONNECTION_RANGE:
                    self.neighbors.append(node)
                    print(f'{self.env.now:.2f} {self.node_id} discovered neighbor {node.node_id} at {distance:.2f} meters')
                    # draw a line between the nodes
                    plt.plot([self.position[0], node.position[0]], [self.position[1], node.position[1]], color='blue', linestyle='--', linewidth=0.5)
        yield self.env.timeout(0)

    def discover_neighbors(self):
        # Initiate neighbor discovery process
        print(f'{self.env.now:.2f} {self.node_id} sends initial DIS broadcast for neighbor discovery')
        yield self.env.timeout(0.1)  # Simulate delay for sending DIS
        for node in self.all_nodes:
            if node != self and self.calculate_distance(node.position) <= CONNECTION_RANGE:
                self.env.process(node.receive_dis(self))

    def send_dio(self):
        while True:
            print(f'{self.env.now:.2f} {self.node_id} sends DIO to neighbors')
            for neighbor in self.neighbors:
                self.env.process(neighbor.receive_dio(self))
            yield self.env.timeout(DIO_INTERVAL)
    
    def receive_dio(self, sender):
        if not self.parent:
            self.parent = sender
            print(f'{self.env.now:.2f} {self.node_id} received DIO from {sender.node_id} and sets as parent')
            # Update network prefix
            self.prefix = f'{sender.prefix}:{int(self.node_id[4:]):02x}'
            print(f'{self.env.now:.2f} {self.node_id} updated prefix to {self.prefix}')
            # Draw a line between the nodes
            plt.plot([self.position[0], sender.position[0]], [self.position[1], sender.position[1]], color='blue', linestyle='--', linewidth=0.5)
            self.send_dao()
        yield self.env.timeout(0)

    def _send_dis(self):
        if not self.neighbors:
            print(f'{self.env.now:.2f} {self.node_id} sends DIS due to no neighbors')
            for node in self.all_nodes:
                if node != self:
                    self.env.process(node.receive_dis(self))
            self.reset_trickle()
        yield self.env.timeout(0.1)
    
    def send_dis(self):
        # Send DIS message to all nodes in the range
        if not self.neighbors:
            print(f'{self.env.now:.2f} {self.node_id} sends DIS due to no neighbors')
            for node in self.all_nodes:
                if node != self and self.calculate_distance(node.position) <= CONNECTION_RANGE:
                    self.env.process(node.receive_dis(self))
            self.reset_trickle()
        yield self.env.timeout(0.1)

    def _receive_dis(self, sender):
        print(f'{self.env.now:.2f} {self.node_id} received DIS from {sender.node_id} and sends DIO')
        self.env.process(sender.receive_dio(self))
        yield self.env.timeout(0.1)

    def receive_dis(self, sender):
        # Receive DIS message from a neighbor and send DIO message
        distance = self.calculate_distance(sender.position)
        if sender not in self.neighbors and distance <= CONNECTION_RANGE:
            self.neighbors.append(sender)
            print(f'{self.env.now:.2f} {self.node_id} received DIS from {sender.node_id}, sends DIO')
            self.env.process(sender.receive_dio(self))
        yield self.env.timeout(0.1)

    def send_dao(self):
        print(f'{self.env.now:.2f} {self.node_id} sends DAO to {self.parent.node_id} with prefix {self.prefix}')
        if self.parent:
            print(f'{self.env.now:.2f} {self.node_id} sends DAO to {self.parent.node_id} with prefix {self.prefix}')
            yield self.env.process(self.parent.receive_dao(self.prefix, self))  # Ensure using 'yield'
    
    def receive_dao(self, prefix, child):
        print(f'{self.env.now:.2f} {self.node_id} received DAO from {child.node_id}, Prefix: {prefix}')
        if self.parent:
            yield self.env.process(self.parent.receive_dao(prefix, self))  # Ensure using 'yield'

        yield self.env.timeout(0)  # Ensure this function is a generator

    def calculate_distance(self, other_position):
        return ((self.position[0] - other_position[0])**2 + (self.position[1] - other_position[1])**2)**0.5
    
    def reset_trickle(self):
        self.I = self.Imin
        self.t = random.uniform(self.Imin, self.I)

    def trickle_timer(self):
        while True:
            yield self.env.timeout(self.t)
            if not self.neighbors:
                self.send_dis()
            self.I = min(self.I * 2, self.Imax)
            self.t = random.uniform(self.Imin, self.I)

def setup_environment(num_nodes, width, height):
    env = simpy.Environment()
    nodes = []

    # Initialize a plot
    plt.figure(figsize=(8, 8))
    plt.title('Node Distribution in RPL Simulation')
    plt.xlabel('Width (meters)')
    plt.ylabel('Height (meters)')

    def create_nodes():
        for i in range(num_nodes):
            position = (round(random.uniform(0, width), 4), round(random.uniform(0, height), 4))

            valid_position = False
            while not valid_position:
                valid_position = True
                for node in nodes:
                    if node.calculate_distance(position) < MINIMUM_DISTANCE:
                        valid_position = False
                        position = (round(random.uniform(0, width), 4), round(random.uniform(0, height), 4))
                        break

            node = Node(env, f'Node{i:02d}', position, nodes)
            nodes.append(node)
            env.process(node.discover_neighbors())
            env.process(node.send_dio())
            env.process(node.trickle_timer())
            print(f'{env.now:.2f} {node.node_id} created at {position}')
            
            # Plot the node position
            c = (random.random(), random.random(), random.random())
            plt.scatter(*position, color=c, label=f'n{i}', s=15)
            # plt.text(position[0], position[1] - 3, f'n{i}', fontsize=7, ha='center', va='bottom', color=c)
            # plt.gca().add_artist(plt.Circle(position, CONNECTION_RANGE, color=c, fill=False, linestyle='--', linewidth=0.3, alpha=0.50))
            
            yield env.timeout(NODE_CREATION_INTERVAL)

    env.process(create_nodes())
    return env, nodes

# Setup and start the simulation
print('RPL Simulation')
env, nodes = setup_environment(NUM_NODES, AREA_WIDTH, AREA_HEIGHT)
env.run(until=60)  # Extend runtime to ensure all nodes are created and can act


# Draw Node Name and Their Prefix
for node in nodes:
    _text = f'{node.node_id.replace("Node", "N")} {node.prefix.replace("2001:db8::", "::")}'
    plt.text(node.position[0], node.position[1] - 3, _text, fontsize=7, ha='center', va='bottom', color='black')

# Show plot
plt.xlim(0, AREA_WIDTH)
plt.ylim(0, AREA_HEIGHT)
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(False)
# plt.show()
plt.savefig('output.png', transparent=False, dpi=300)
plt.close()
