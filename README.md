# RPL Simulation

This project simulates the Routing over Low Power and Lossy Networks (RPL) protocol using the SimPy discrete event simulation framework. The simulation is designed to visualize the Dynamic Objective Directed Acyclic Graph (DODAG) formation process using RPL's DIS, DIO, and DAO messaging mechanisms.

## Overview

The simulation models a network of nodes distributed within a defined area. Each node attempts to discover neighbors and build a routing structure based on the RPL protocol specifications. The key features demonstrated include neighbor discovery, DODAG formation, and network prefix distribution using DAO messages.

## Simulation Details

- **Random Seed**: Customizable to achieve different random node distributions.
- **Number of Nodes**: 50
- **Area Dimensions**: 125m x 125m
- **Connection Range**: Each node has a connection range of 25 meters.
- **DIO Interval**: DIO messages are sent every 5 seconds.
- **Node Creation Interval**: Nodes are created with a 1-second interval between each to simulate gradual network population.

### Key Components

- **Node**: Represents a network device participating in the RPL network.
  - Each node broadcasts a DIS message upon creation to discover neighbors.
  - Nodes respond to DIS messages from other nodes within their connection range with a DIO message.
  - The network topology is established based on the reception of DIO messages, where nodes select their parent to form the DODAG structure.
  - DAO messages are used to propagate routing prefix information up the DODAG.

- **Trickle Algorithm**: Implemented to manage the timing of DIS messages, increasing efficiency and reducing network chatter.

## Requirements

- Python 3.6 or higher
- SimPy
- Matplotlib

## Usage

To run the simulation, execute the script `simulation.py`:

```bash
python simulation.py
```

The simulation will generate a plot showing the node distribution and the DODAG connections. Additionally, diagnostic outputs including node creation, neighbor discovery, and message exchanges are printed to the console and saved to a file named simulation.txt.

## Visualization
The generated plot will illustrate nodes as points on a grid with lines connecting them to represent parent-child relationships in the DODAG. Each node's ID and the IPv6 prefix are displayed next to the corresponding node on the plot.

## Output
* A PNG image of the node distribution and connections named output.png.
* A detailed log of the simulation process saved to output.txt, including timestamped events such as DIS and DIO message exchanges, and DAO message propagation.

## Documentation
**TBD**

## Authors
[Arman](https://github.com/arman-bd) and Team

## License
This project is licensed under the MIT License.

## Acknowledgments
[Aarhus University](https://au.dk) - For providing the academic environment and guidance necessary for this project.