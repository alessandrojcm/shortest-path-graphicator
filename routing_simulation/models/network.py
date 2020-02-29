from dataclasses import dataclass, field
from typing import List, Tuple

from networkx import Graph
from simpy import Environment, FilterStore, Resource

from routing_simulation.models.router import Router
from routing_simulation.models.link import Link


@dataclass()
class Network:
    env: Environment
    available_links: FilterStore
    pending_messages: FilterStore
    sent_messages: Resource
    topology: Graph = field(default=None)
    random_graph: Tuple[int, int] = field(default=None)
    MAX_WEIGHT = 5000

    def __post_init__(self):
        if self.topology is None and self.random_graph:
            from networkx import random_regular_graph
            m, n = self.random_graph
            self.topology = random_regular_graph(m, n)
        self.__init_nodes()
        self.__init_edges()

    def send_frame(self, data: List[int], origin: int, destination: int):
        from routing_simulation.models.message import Message

        start_node = self.topology.nodes[origin]['data']
        if start_node is None:
            raise RuntimeError('Invalid start node')

        self.env.process(start_node.send_message(Message(origin, destination, data)))

        for i in self.topology.nodes:
            node = self.topology.nodes[i]['data']
            if node.name == origin:
                pass
            self.env.process(node.receive())
        self.env.run()

    def __init_nodes(self):
        from networkx import bellman_ford_path, set_node_attributes

        node_mappings = {
            k: Router(self.env, self.topology, self.available_links, self.pending_messages, self.sent_messages, k,
                      bellman_ford_path) for k in range(self.topology.number_of_nodes())
        }
        set_node_attributes(self.topology, node_mappings, 'data')

    def __init_edges(self):
        from random import randint
        from networkx import set_edge_attributes
        edge_mappings = {
            (s, d): Link(d if d else randint(self.MAX_WEIGHT), (s, d)).to_dict() for s, d, data in
            self.topology.edges.data()
        }
        set_edge_attributes(self.topology, edge_mappings)
