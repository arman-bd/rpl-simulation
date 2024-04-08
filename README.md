# RPL Protocol Simulation with SimPy

This project simulates the Routing Protocol for Low-Power and Lossy Networks (RPL) using the process-based discrete-event simulation framework SimPy. The main goal is to model the behavior of nodes within an RPL network and their interactions through the use of standard RPL messages (DIO, DIS, and DAO) for the establishment and maintenance of a DODAG.

## Features

- **Neighbor Discovery**: Nodes can discover their immediate neighbors, emulating the physical layer of a real IoT network.
- **DODAG Formation**: Nodes use DIO messages to form a Destination-Oriented Directed Acyclic Graph based on simulated metrics.
- **DAO Propagation**: The simulation includes the propagation of DAO messages for upward routing within the network.
- **Trickle Timer**: An implementation of the Trickle algorithm to efficiently manage the transmission of control messages.

## Getting Started

### Prerequisites

- Python 3.6 or newer

### Installation

Install SimPy using pip:

```sh
pip install simpy
```

Running the Simulation
To run the simulation, navigate to the project directory and run:

```sh
python rpl_simulation.py
```

### Simulation Design
The simulation consists of the following components:

- **Node**: Represents a network node with the ability to send and receive RPL messages.
- **Network**: Manages the collection of nodes and simulates the network layer.

Nodes in the network periodically send DIO messages to build a DODAG. The simulation currently assigns random ranks to nodes for demonstration purposes.

## Contributing
If you would like to contribute to the development of this RPL simulation, please follow these steps:

- Fork the repository.
- Create your feature branch (`git checkout -b feature/amazing-feature`).
- Commit your changes (`git commit -m 'Added Some Amazing Feature'`).
- Push to the branch (`git push origin feature/amazing-feature`).
- Open a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Authors
Arman Hossain - Initial work - github.com/arman-bd

## Acknowledgments
- SimPy Developers for the fantastic simulation framework.
- The IETF for the specifications of the RPL protocol.
- Contributors and maintainers of RFC 6550 and RFC 6206.

## References
- [SimPy Documentation](https://simpy.readthedocs.io/)
- RFC 6550 - RPL: IPv6 Routing Protocol for Low-Power and Lossy Networks
- RFC 6206 - The Trickle Algorithm