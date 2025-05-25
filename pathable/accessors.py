"""Pathable accessors module"""
from collections.abc import Hashable
from collections.abc import Iterator
from collections.abc import Mapping
from contextlib import contextmanager
from functools import lru_cache
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

    _lookup_refs: dict[int, Mapping[Hashable, Any]] = {}

    def __init__(self, lookup: Mapping[Hashable, Any]):
        self.lookup = lookup

        LookupAccessor._lookup_refs[id(lookup)] = lookup

    def stat(self, parts: list[Hashable]) -> dict[str, Any]:
        raise NotImplementedError

    def keys(self, parts: list[Hashable]) -> Any:
        with self.open(parts) as d:
            if isinstance(d, Mapping):
                return d.keys()
            if isinstance(d, list):
                return list(range(len(d)))
            raise AttributeError

    def len(self, parts: list[Hashable]) -> int:
        with self.open(parts) as d:
            return len(d)

    @classmethod
    @lru_cache(maxsize=None)
    def _open_lookup(cls, lookup_id: int, parts: tuple[Hashable, ...]) -> Any:
        lookup = cls._lookup_refs[lookup_id]
        content = lookup
        for part in parts:
            content = content[part]
        return content

    @contextmanager
    def open(
        self, parts: list[Hashable]
    ) -> Iterator[Union[Mapping[Hashable, Any], Any]]:
        content = self._open_lookup(id(self.lookup), tuple(parts))
        try:
            yield content
        finally:
            pass
