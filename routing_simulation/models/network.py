from dataclasses import dataclass, field
from typing import List, Tuple

from networkx import Graph
from simpy import FilterStore, Store, Environment

from routing_simulation.models.link import Link
from routing_simulation.models.router import Router


@dataclass()
class Network:
    env: Environment
    available_links: FilterStore
    pending_messages: FilterStore
    sent_messages: Store
    log: Store
    topology: Graph = field(default=None)
    random_graph: Tuple[int, int] = field(default=None)
    MAX_WEIGHT = 5000

    def __post_init__(self):
        if self.topology is None and self.random_graph:
            from networkx import random_regular_graph
            m, n = self.random_graph
            self.topology = random_regular_graph(m, n)
        elif self.topology is not None:
            self.__init_nodes()
            self.__init_edges()

    def init_random_graph(self, random_graph: Tuple[int, int] = (4, 10)):
        from networkx import random_regular_graph
        m, n = random_graph
        self.topology = random_regular_graph(m, n)
        self.__init_nodes()
        self.__init_edges()

    def set_frame(self, data: List[int], origin: int, destination: int):
        from routing_simulation.models.message import Message

        start_node = self.topology.nodes[origin]['data']
        if start_node is None:
            raise RuntimeError('Invalid start node')

        self.env.process(start_node.send_message(Message(origin, origin, destination, data)))

        for i in self.topology.nodes:
            node = self.topology.nodes[i]['data']
            if node.name == origin:
                pass
            self.env.process(node.receive())

    def start(self):
        return self.env.run()

    def __init_nodes(self):
        from networkx import bellman_ford_path, set_node_attributes

        node_mappings = {
            k: Router(self.env, self.topology, self.available_links, self.pending_messages, self.sent_messages,
                      self.log, k,
                      bellman_ford_path) for k in range(self.topology.number_of_nodes())
        }
        set_node_attributes(self.topology, node_mappings, 'data')

    def __init_edges(self):
        from random import randint
        from networkx import set_edge_attributes
        edge_mappings = {
            (s, d): Link(d if d else randint(0, self.MAX_WEIGHT), (s, d)).to_dict() for s, d, data in
            self.topology.edges.data()
        }
        set_edge_attributes(self.topology, edge_mappings)


def network_setup(realtime=False):
    import simpy
    if not realtime:
        env = simpy.Environment()
    else:
        env = simpy.RealtimeEnvironment(strict=False, factor=2)
    available_links = simpy.FilterStore(env)
    pending_messages = simpy.FilterStore(env)
    send_messages = simpy.Store(env)
    log = simpy.Store(env)

    return Network(env, available_links, pending_messages, send_messages, log)
