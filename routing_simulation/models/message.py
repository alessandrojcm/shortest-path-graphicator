from dataclasses import dataclass, field
from typing import List


@dataclass()
class Message:
    original_node: int
    origin: int
    destination: int
    data: List[int]
    next_node: int = field(default=None)
    link: int = field(default=None)
