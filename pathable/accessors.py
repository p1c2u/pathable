"""Pathable accessors module"""
from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Hashable
from typing import Iterator
from typing import List
from typing import Mapping
from typing import Union


class LookupAccessor:
    """Accessor for object that supports __getitem__ lookups"""

    def __init__(self, lookup: Mapping[Hashable, Any]):
        self.lookup = lookup

    def stat(self, parts: List[Hashable]) -> Dict[str, Any]:
        raise NotImplementedError

    def keys(self, parts: List[Hashable]) -> Any:
        with self.open(parts) as d:
            return d.keys()

    def len(self, parts: List[Hashable]) -> int:
        with self.open(parts) as d:
            return len(d)

    @contextmanager
    def open(
        self, parts: List[Hashable]
    ) -> Iterator[Union[Mapping[Hashable, Any], Any]]:
        content = self.lookup
        for part in parts:
            content = content[part]
        try:
            yield content
        finally:
            pass
