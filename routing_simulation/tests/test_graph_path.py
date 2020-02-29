import pytest

from routing_simulation import Network

MAX_NODES = 10


@pytest.fixture()
def graph():
    import networkx as nx
    graph = nx.generators.mycielski.mycielski_graph(MAX_NODES)
    edge_weights = {k: {'weight': i ** 2} for i, k in enumerate(graph.edges)}
    nx.set_edge_attributes(graph, edge_weights)

    return graph


@pytest.fixture()
def simpy_env():
    import simpy
    env = simpy.Environment()
    available_links = simpy.FilterStore(env)
    pending_messages = simpy.FilterStore(env)
    sent_messages = simpy.Resource(env)

    return env, available_links, pending_messages, sent_messages


def test_simulation(simpy_env, graph):
    env, links, messages, sent_messages = simpy_env
    network = Network(env, links, messages, sent_messages, graph)

    network.send_frame([1, 1, 1], 0, MAX_NODES)
