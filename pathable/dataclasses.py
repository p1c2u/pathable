from collections.abc import Hashable
from dataclasses import dataclass


@dataclass
class BasePathData:

    parts: list[Hashable]
    separator: str
