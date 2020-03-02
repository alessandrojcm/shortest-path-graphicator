from dataclasses import dataclass, field, asdict
from typing import Tuple

# Data bag to represent a link
@dataclass()
class Link:
    weight: int
    # Link name is represented as the tuple (start, end) meaning the pair of nodes connected by the edge.
    name: Tuple[int, int]
    busy: bool = field(default=False)
    error: bool = field(default=False)

    def to_dict(self):
        return asdict(self)
