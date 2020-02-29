from dataclasses import dataclass, replace, asdict
from typing import List, Callable

from networkx import Graph
from simpy import FilterStore, Environment, Interrupt, Store

from routing_simulation.models.message import Message


@dataclass()
class Router:
    env: Environment
    topology: Graph
    available_links: FilterStore
    pending_messages: FilterStore
    sent_messages: Store
    name: int
    shortest_path: Callable[[int, int], List[int]]

    def __hash__(self):
        return self.name

    def __iter__(self):
        return iter(asdict(self))

    def as_dict(self):
        return asdict(self)

    def send_message(self, message: Message):
        try:
            if not message.next_node and message.origin != self.name:
                self.env.exit()
            next_node = self.shortest_path(self.topology, message.origin, message.destination)[1]
            out_link = self.__take_link(message.origin, next_node)
            out_message = replace(message, next_node=next_node, link=out_link)
            print('Sending message {d} from node {o} to node {fn} through link {l}'.format(
                d=out_message.data,
                o=out_message.origin,
                fn=out_message.destination,
                l=out_message.link
            ))
            yield self.pending_messages.put(out_message)
        except Interrupt as err:
            from sys import stderr
            stderr.write(err)

    def receive(self):
        while True:
            try:
                inbound_message = yield self.pending_messages.get(lambda m: m.next_node == self.name)
                self.available_links.put(inbound_message.link)
                if inbound_message.destination != self.name:
                    print('{i} node resent message {d} from node {p} to node {fn} through link {l}'.format(
                        i=self.name,
                        d=inbound_message.data,
                        p=inbound_message.origin,
                        fn=inbound_message.destination,
                        l=inbound_message.link
                    ))
                    self.env.process(self.send_message(replace(inbound_message, origin=self.name)))
                else:
                    yield self.sent_messages.put(inbound_message)

            except Interrupt as err:
                from sys import stderr
                stderr.write(err)

    def __take_link(self, origin, destination):
        out_link = self.topology.edges[origin, destination]['name']
        self.available_links.get(lambda l: l == out_link)
        return out_link
