"""Pathable accessors module"""
from collections.abc import Hashable
from collections.abc import Iterator
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any
from typing import Union


class BaseAccessor:
    """Base accessor."""

    def stat(self, parts: list[Hashable]) -> dict[str, Any]:
        raise NotImplementedError

    def keys(self, parts: list[Hashable]) -> Any:
        raise NotImplementedError

    def len(self, parts: list[Hashable]) -> int:
        raise NotImplementedError

    @contextmanager
    def open(
        self, parts: list[Hashable]
    ) -> Iterator[Union[Mapping[Hashable, Any], Any]]:
        raise NotImplementedError


class LookupAccessor(BaseAccessor):
    """Accessor for object that supports __getitem__ lookups"""

    def __init__(self, lookup: Mapping[Hashable, Any]):
        self.lookup = lookup

    def stat(self, parts: list[Hashable]) -> dict[str, Any]:
        raise NotImplementedError

    def keys(self, parts: list[Hashable]) -> Any:
        with self.open(parts) as d:
            return d.keys()

    def len(self, parts: list[Hashable]) -> int:
        with self.open(parts) as d:
            return len(d)

    @contextmanager
    def open(
        self, parts: list[Hashable]
    ) -> Iterator[Union[Mapping[Hashable, Any], Any]]:
        content = self.lookup
        for part in parts:
            content = content[part]
        try:
            yield content
        finally:
            pass
