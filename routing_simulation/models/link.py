from dataclasses import dataclass, field, asdict
from typing import Tuple


@dataclass()
class Link:
    weight: int
    name: Tuple[int, int]
    busy: bool = field(default=False)
    error: bool = field(default=False)

    def to_dict(self):
        return asdict(self)
