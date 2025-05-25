"""Pathable accessors module"""
from collections.abc import Hashable
from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import Sequence
from contextlib import contextmanager
from functools import lru_cache
from typing import Any
from typing import cast
from typing import Generic
from typing import TypeVar
from typing import Union

from pathable.protocols import Subscriptable

SK = TypeVar('SK', bound=Hashable)
SV = TypeVar('SV')
CSK = TypeVar('CSK', bound=Hashable)
CSV = TypeVar('CSV')


class BaseAccessor:
    """Base accessor."""

    def stat(self, parts: Sequence[Hashable]) -> dict[str, Any]:
        raise NotImplementedError

    def keys(self, parts: Sequence[Hashable]) -> Sequence[Any]:
        raise NotImplementedError

    def len(self, parts: Sequence[Hashable]) -> int:
        raise NotImplementedError

    @contextmanager
    def open(self, parts: Sequence[Hashable]) -> Iterator[Any]:
        raise NotImplementedError


class SubscriptableAccessor(BaseAccessor, Generic[SK, SV]):
    """Accessor for subscriptable content."""

    def __init__(self, content: Subscriptable[SK, SV]):
        self.content = content

    def keys(self, parts: Sequence[Hashable]) -> Sequence[SK]:
        raise NotImplementedError

    @classmethod
    def _open(cls, content: Subscriptable[SK, SV], parts: Sequence[Hashable]) -> Union[SV, Subscriptable[SK, SV]]:
        result: Union[SV, Subscriptable[SK, SV]] = content
        for part in parts:
            part = cast(SK, part)
            # content not travelable
            if not isinstance(result, Subscriptable):
                raise ValueError
            # content trvelable but has no specific part
            if not part in result:
                raise KeyError
            result = result[part]
        return result

    @contextmanager
    def open(
        self, parts: Sequence[Hashable]
    ) -> Iterator[Union[Subscriptable[SK, SV], Any]]:
        try:
            yield self._open(self.content, parts)
        finally:
            pass


class CachedSubscriptableAccessor(SubscriptableAccessor[CSK, CSV], Generic[CSK, CSV]):

    _content_refs: dict[int, Subscriptable[CSK, CSV]] = {}

    def __init__(self, content: Subscriptable[CSK, CSV]):
        super().__init__(content)

        self._content_refs[id(content)] = content

    @classmethod
    @lru_cache(maxsize=None)
    def _open_content_id(cls, content_id: int, parts: Sequence[Hashable]) -> Union[CSV, Subscriptable[CSK, CSV]]:
        content: Subscriptable[CSK, CSV] = cls._content_refs[content_id]
        return super()._open(content, parts)

    @classmethod
    def _open(cls, content: Subscriptable[CSK, CSV], parts: Sequence[Hashable]) -> Union[CSV, Subscriptable[CSK, CSV]]:
        return cls._open_content_id(id(content), parts)


class LookupAccessor(CachedSubscriptableAccessor[Union[str, int], Any]):

    def keys(self, parts: Sequence[Hashable]) -> Sequence[Union[str, int]]:
        with self.open(parts) as d:
            if isinstance(d, Mapping):
                return list(d.keys())
            if isinstance(d, list):
                return list(range(len(d)))
            raise AttributeError

    def len(self, parts: Sequence[Hashable]) -> int:
        with self.open(parts) as d:
            return len(d)
