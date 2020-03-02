from dataclasses import dataclass, replace, asdict
from typing import List, Callable

from networkx import Graph
from simpy import FilterStore, Environment, Interrupt, Store

from routing_simulation.models.message import Message


# Class that represents a router with send a receive methods
@dataclass()
class Router:
    # Simpy environment
    env: Environment
    # Router must be aware of the topology
    topology: Graph
    # Same as Network
    available_links: FilterStore
    # Same as Network
    pending_messages: FilterStore
    # Same as Network
    sent_messages: Store
    # Same as Network
    log: Store
    # Label of the node
    name: int
    shortest_path: Callable[[int, int], List[int]]

    def __hash__(self):
        return self.name

    def __iter__(self):
        return iter(asdict(self))

    def as_dict(self):
        return asdict(self)

    def send_message(self, message: Message, resent=False):
        # Process for package sending
        try:
            # Get the next node in the shortest pat
            next_node = self.shortest_path(self.topology, message.origin, message.destination)[1]
            # Set link as busy
            out_link = self.__take_link(message.origin, next_node)
            out_message = replace(message, next_node=next_node, link=out_link)
            if not resent:
                # Store operation in log
                self.log.put('Sending message {d} from node {o} to node {fn} through link {l}'.format(
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
        try:
            # Check for pending messages incoming to this node
            with self.pending_messages.get(lambda m: m.next_node == self.name) as g:
                inbound_message = yield g
                # Release the link
                self.available_links.put(inbound_message.link)
                # Check if this is the message's final destination, if not relay to the next node in path
                if inbound_message.destination != self.name:
                    # Store operation in log
                    self.log.put('Node {i} resent message {d} from node {p} to node {fn} through link {l}'.format(
                        i=self.name,
                        d=inbound_message.data,
                        p=inbound_message.origin,
                        fn=inbound_message.destination,
                        l=inbound_message.link
                    ))
                    # Resend the message
                    self.env.process(self.send_message(replace(inbound_message, origin=self.name), resent=True))
                else:
                    # Store operation in log
                    yield self.log.put('{i} node received message {d} from node {p} through link {l}'.format(
                        i=self.name,
                        d=inbound_message.data,
                        p=inbound_message.origin,
                        l=inbound_message.link
                    ))

        except Interrupt as err:
            from sys import stderr
            stderr.write(err)

    def __take_link(self, origin, destination):
        out_link = self.topology.edges[origin, destination]['name']
        self.available_links.get(lambda l: l == out_link)
        return out_link
