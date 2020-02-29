import networkx as nx
import simpy

from routing_simulation import Network

MAX_NODES = 10

graph = nx.generators.mycielski.mycielski_graph(MAX_NODES)
edge_weights = {k: {'weight': i ** 2} for i, k in enumerate(graph.edges)}

env = simpy.Environment()
available_links = simpy.FilterStore(env)
pending_messages = simpy.FilterStore(env)
sent_messages = simpy.Store(env)

nx.set_edge_attributes(graph, edge_weights)

network = Network(env, available_links, pending_messages, sent_messages, graph)


def print_messages(finished_messages):
    with finished_messages.get() as rq:
        fm = yield rq
        if fm is not None:
            print('Received message {d} from node {n} through link {l}'.format(d=fm.data, n=fm.origin, l=fm.link))


env.process(print_messages(sent_messages))
network.send_frame([1, 1, 1], 0, MAX_NODES)
