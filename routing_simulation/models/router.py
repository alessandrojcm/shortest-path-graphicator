from dataclasses import dataclass, replace, asdict
from typing import List, Callable

from networkx import Graph
from simpy import FilterStore, Environment, Interrupt, Resource

from routing_simulation.models.message import Message


@dataclass()
class Router:
    env: Environment
    topology: Graph
    available_links: FilterStore
    pending_messages: FilterStore
    sent_messages: Resource
    name: int
    shortest_path: Callable[[int, int], List[int]]

    def __post_init__(self):
        self.shortest_path = lambda o, d: self.shortest_path(self.topology, o, d)

    def __hash__(self):
        return self.name

    def __iter__(self):
        return iter(asdict(self))

    def as_dict(self):
        return asdict(self)

    def send_message(self, message: Message):
        try:
            if not message.next_node:
                self.env.exit()
            next_node = self.shortest_path(message.origin, message.destination)[0]
            out_link = self.__take_link(message.origin, next_node)
            yield self.pending_messages.put(
                replace(message, next_node=next_node, link=out_link)
            )
        except Interrupt as err:
            from sys import stderr
            stderr.write(err)

    def receive(self):
        try:
            inbound_message = yield self.pending_messages.get(lambda m: m.next_node == self.name)
            self.available_links.put(inbound_message.link)
            if inbound_message.destination != self.name:
                self.send_message(inbound_message)
            else:
                self.sent_messages.put(inbound_message)

        except Interrupt as err:
            from sys import stderr
            stderr.write(err)

    def __take_link(self, origin, destination):
        out_link = self.topology.edges[origin, destination]['name']
        self.available_links.get(lambda l: l['name'] == out_link)
        return out_link
