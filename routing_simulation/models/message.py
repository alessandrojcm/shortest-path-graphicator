from dataclasses import dataclass, field
from typing import List

# Data bag to represent a message
@dataclass()
class Message:
    original_node: int
    origin: int
    destination: int
    data: List[int]
    # Next node in the shortest path
    next_node: int = field(default=None)
    # Link on which the message is transmitted
    link: int = field(default=None)
