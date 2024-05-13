import os
import builtins
import random
import simpy
import matplotlib.pyplot as plt

# Delete output files if they exist
for filename in ['output.txt', 'output.png']:
    if os.path.exists(filename):
        os.remove(filename)

# Function to log messages to a file and print them to stdout
def log(*args, **kwargs):
    with open('output.txt', 'a') as f:
        builtins.print(*args, **kwargs, file=f)
    builtins.print(*args, **kwargs)

# Function to configure simulation parameters
def configure_simulation():
    print("Using default simulation parameters")
    config = {
        "RANDOM_SEED": 1111,
        "NUM_NODES": 50,
        "AREA_WIDTH": 125,
        "AREA_HEIGHT": 125,
        "MINIMUM_DISTANCE": 5,
        "CONNECTION_RANGE": 15,
        "DIO_INTERVAL": 10,
        "NODE_CREATION_INTERVAL": 1,
        "RUNTIME": 120
    }
    configure = input("Do you want to configure simulation parameters? y/[N]: ")
    if configure.lower() == 'y':
        config["RANDOM_SEED"] = int(input("Enter Random Seed [1111]: ") or config["RANDOM_SEED"])
        config["NUM_NODES"] = int(input("Enter Number of Nodes [50]: ") or config["NUM_NODES"])
        config["AREA_WIDTH"] = int(input("Enter Area Width in Meters [125]: ") or config["AREA_WIDTH"])
        config["AREA_HEIGHT"] = int(input("Enter Area Height in Meters [125]: ") or config["AREA_HEIGHT"])
        config["MINIMUM_DISTANCE"] = int(input("Enter Minimum Distance Between Nodes in Meters [5]: ") or config["MINIMUM_DISTANCE"])
        config["CONNECTION_RANGE"] = int(input("Enter Connection Range in Meters [15]: ") or config["CONNECTION_RANGE"])
        config["DIO_INTERVAL"] = int(input("Enter DIO Interval in Seconds [10]: ") or config["DIO_INTERVAL"])
        config["NODE_CREATION_INTERVAL"] = int(input("Enter Node Creation Interval in Seconds [1]: ") or config["NODE_CREATION_INTERVAL"])
        config["RUNTIME"] = int(input("Enter Simulation Runtime in Seconds [120]: ") or config["RUNTIME"])
    return config

# Initialize random seed
config = configure_simulation()
random.seed(config["RANDOM_SEED"])

class Node:
    def __init__(self, env, node_id, position, all_nodes):
        # Environment
        self.env = env

        # Node Information
        self.parent = None
        self.node_id = node_id
        self.position = position
        self.all_nodes = all_nodes
        self.neighbors = []
        self.lost_neighbors = []

        # Network Prefix
        self.prefix = f'2001:db8::{int(node_id[4:]):02x}'

        # Trickle Parameters
        self.Imin = 1
        self.Imax = 10
        self.I = self.Imin
        self.t = random.uniform(self.Imin, self.I)

        # Color for Plotting
        self.color = (random.random(), random.random(), random.random())

    def discover_neighbors(self):
        # Initiate neighbor discovery process
        log(f'{self.env.now:.2f} {self.node_id} starting neighbor discovery')
        yield self.env.timeout(0.1)  # Simulate delay for sending DIS
        for node in self.all_nodes:
            if node != self and self.calculate_distance(node.position) <= config["CONNECTION_RANGE"]:
                self.env.process(node.receive_dis(self))
                log(f'{self.env.now:.2f} {self.node_id} sends DIS to {node.node_id}')

    def send_dio(self):
        # Send DIO message to all neighbors
        while True:
            for neighbor in self.neighbors:
                if neighbor.parent != self:
                    self.env.process(neighbor.receive_dio(self))
                    log(f'{self.env.now:.2f} {self.node_id} sends DIO to {neighbor.node_id}')
            yield self.env.timeout(config["DIO_INTERVAL"])
    
    def receive_dio(self, sender):
        own_prefix = f':{int(self.node_id[4:]):02x}'
        cycle = False
        if own_prefix in sender.prefix:
            cycle = True
        # Receive DIO message from a neighbor, avoid cycles
        if cycle == False:
            if not self.parent:
                # Update parent and prefix
                self.parent = sender
                self.prefix = f'{sender.prefix}:{int(self.node_id[4:]):02x}'
                yield self.env.process(self.send_dao())
                log(f'{self.env.now:.2f} {self.node_id} received DIO from new parent {sender.node_id}; new prefix: {self.prefix}')
            else:
                # Check if sender is a Closer parent
                if sender.parent != self and self.calculate_distance(sender.position) < self.calculate_distance(self.parent.position) and sender.parent != self:
                    # Update parent and prefix
                    self.parent = sender
                    self.prefix = f'{sender.prefix}:{int(self.node_id[4:]):02x}'
                    yield self.env.process(self.send_dao())
                    log(f'{self.env.now:.2f} {self.node_id} received DIO from closer parent {sender.node_id}; new prefix: {self.prefix}')

        yield self.env.timeout(0)
    
    def send_dis(self):
        if not self.neighbors:
            for node in self.all_nodes:
                if node != self and self.calculate_distance(node.position) <= config["CONNECTION_RANGE"]:
                    self.env.process(node.receive_dis(self))
        yield self.env.timeout(0)

    def receive_dis(self, sender):
        # Receive DIS message from a neighbor and send DIO message
        distance = self.calculate_distance(sender.position)
        if sender not in self.neighbors and distance <= config["CONNECTION_RANGE"]:
            self.neighbors.append(sender) if sender not in self.neighbors else None
            sender.neighbors.append(self) if self not in sender.neighbors else None
            self.env.process(sender.receive_dio(self))
            log(f'{self.env.now:.2f} {self.node_id} received DIS from {sender.node_id}; new neighbor: {sender.node_id}')
        yield self.env.timeout(0.1)

    def send_dao(self):
        # Send DAO message to parent
        if self.parent:
            log(f'{self.env.now:.2f} {self.node_id} sends DAO to {self.parent.node_id}, Prefix: {self.prefix}')
            yield self.env.process(self.parent.receive_dao(self.prefix, self))  # Ensure using 'yield'
    
    def receive_dao(self, prefix, child):
        # Reject route if cycle detected
        child_prefix = f':{int(child.node_id[4:]):02x}'
        cycle = False
        if child_prefix in prefix:
            log(f'{self.env.now:.2f} {self.node_id} received DAO from {child.node_id} with cycle, Prefix: {prefix}')
            cycle = True
        # Receive DAO message from child and forward to parent
        if self.parent and not cycle:
            child.prefix = f'{child.parent.prefix}:{int(child.node_id[4:]):02x}'
            self.env.process(self.parent.receive_dao(prefix, self))
            log(f'{self.env.now:.2f} {self.node_id} received DAO from {child.node_id}, Prefix: {prefix}')

        yield self.env.timeout(0)  # Ensure this function is a generator

    def calculate_distance(self, other_position):
        # Calculate distance between this node and another node
        return ((self.position[0] - other_position[0])**2 + (self.position[1] - other_position[1])**2)**0.5
    
    def reset_trickle(self):
        # Reset Trickle parameters
        self.I = self.Imin
        self.t = random.uniform(self.Imin, self.I)

    def trickle_timer(self):
        # Trickle timer for sending DIS messages
        while True:
            yield self.env.timeout(self.t)
            if not self.neighbors:
                yield self.env.process(self.send_dis())
                log(f'{self.env.now:.2f} {self.node_id} sends DIS broadcast for neighbor discovery')
            self.I = min(self.I * 2, self.Imax)
            self.t = random.uniform(self.Imin, self.I)

    def network_disruption(self):
        # Simulate network disruption by removing all neighbors 
        # 1/20 chances of network disruption every 5 seconds
        while True:
            yield self.env.timeout(self.t)
            if random.random() < (1/100):
                log(f'{self.env.now:.2f} {self.node_id} network disruption')
                self.lost_neighbors.clear()

                # Remove self from neighbors
                for neighbor in self.neighbors:
                    if self in neighbor.neighbors:
                        neighbor.neighbors.remove(self)
                
                # Add all neighbors to lost_neighbors
                for neighbor in self.neighbors:
                    self.lost_neighbors.append(neighbor)
                
                # Clear neighbors
                self.neighbors.clear()

                # Re-Discover neighbors
                yield self.env.process(self.discover_neighbors())

def setup_environment(num_nodes, width, height):
    env = simpy.Environment()
    nodes = []

    def create_nodes():
        for i in range(num_nodes):
            position = (round(random.uniform(0, width), 4), round(random.uniform(0, height), 4))

            valid_position = False
            while not valid_position:
                valid_position = True
                for node in nodes:
                    if node.calculate_distance(position) < config["MINIMUM_DISTANCE"]:
                        valid_position = False
                        position = (round(random.uniform(0, width), 4), round(random.uniform(0, height), 4))
                        break

            node = Node(env, f'Node{i:02d}', position, nodes)
            nodes.append(node)
            env.process(node.discover_neighbors())
            env.process(node.send_dio())
            env.process(node.trickle_timer())
            env.process(node.network_disruption())
            log(f'{env.now:.2f} {node.node_id} created at {node.position}')
            
            yield env.timeout(config["NODE_CREATION_INTERVAL"])

    env.process(create_nodes())
    return env, nodes

# Setup and start the simulation
print('RPL Simulation')
env, nodes = setup_environment(config["NUM_NODES"], config["AREA_WIDTH"], config["AREA_HEIGHT"])
env.run(until=config["RUNTIME"])  # Extend runtime to ensure all nodes are created and can act


# Initialize a plot
plt.figure(figsize=(8, 8))
plt.title('Node Distribution in RPL Simulation')
plt.xlabel('Width (meters)')
plt.ylabel('Height (meters)')

drawn_pair = []
for node in nodes:
    plt.scatter(node.position[0], node.position[1], color=node.color, label=node.node_id)
    # circle = plt.Circle(node.position, config["CONNECTION_RANGE"], color=node.color, fill=False, alpha=0.1, linestyle='dotted', linewidth=0.25)
    # plt.gca().add_artist(circle)

    # Node Name
    node_name = node.node_id.replace('Node', 'N') + '\n' + node.prefix.replace('2001:db8::', '::')
    bottom_padding = int(config["AREA_HEIGHT"]) * 0.05
    plt.text(node.position[0], node.position[1] - bottom_padding, node_name, fontsize=6, ha='center', va='bottom', color=node.color)

    
    connected_neighbors = [neighbor for neighbor in node.neighbors if neighbor in nodes]
    for neighbor in connected_neighbors:
        if (node.node_id, neighbor.node_id) in drawn_pair or (neighbor.node_id, node.node_id) in drawn_pair:
            continue
        plt.plot([node.position[0], neighbor.position[0]], [node.position[1], neighbor.position[1]], color='blue', alpha=0.75, linestyle='dotted', linewidth=0.75)
        drawn_pair.append((node.node_id, neighbor.node_id))

    # Currently Lost Neighbors: lost_neighbors - neighbors
    lost_neighbors = [neighbor for neighbor in node.lost_neighbors] # if neighbor not in connected_neighbors]
    for neighbor in lost_neighbors:
        # if (node, neighbor) in drawn_pair or (neighbor, node) in drawn_pair:
        #     continue
        plt.plot([node.position[0], neighbor.position[0]], [node.position[1], neighbor.position[1]], color='red', alpha=0.25, linestyle='solid', linewidth=0.75)
        drawn_pair.append((node, neighbor))

# Show plot
plt.xlim(0, config["AREA_WIDTH"])
plt.ylim(0, config["AREA_HEIGHT"])
plt.gca().set_aspect('equal', adjustable='box')
plt.grid(False)
plt.savefig('output.png', transparent=False, dpi=300)
plt.close()