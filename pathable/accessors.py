"""Pathable accessors module"""
from collections.abc import Hashable
from collections.abc import Mapping
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import Union

from pyrsistent import pdeque
from pyrsistent import PDeque

from pathable.protocols import Subscriptable
from pathable.types import LookupKey
from pathable.types import LookupValue
from pathable.types import LookupNode

K = TypeVar('K', bound=Hashable, contravariant=True)
V = TypeVar('V', covariant=True)
N = TypeVar('N')
SK = TypeVar('SK', bound=Hashable, contravariant=True)
SV = TypeVar('SV', covariant=True)
CSK = TypeVar('CSK', bound=Hashable, contravariant=True)
CSV = TypeVar('CSV', covariant=True)


class NodeAccessor(Generic[N, K, V]):
    """Node accessor."""

    def __init__(self, node: N):
        self.node = node

    def __eq__(self, other: object) -> Any:
        if not isinstance(other, NodeAccessor):
            return NotImplemented
        return self.node == other.node

    def stat(self, parts: Sequence[K]) -> dict[str, Any]:
        raise NotImplementedError

    def keys(self, parts: Sequence[K]) -> Sequence[K]:
        raise NotImplementedError

    def len(self, parts: Sequence[K]) -> int:
        raise NotImplementedError

    def read(self, parts: Sequence[K]) -> V:
        node = self._get_node(self.node, pdeque(parts))
        return self._read_node(node)

    @classmethod
    def _get_node(cls, node: N, parts: PDeque[K]) -> N:
        try:
            part, parts = cls._pop_next_part(parts)
        except IndexError:
            return node

        subnode = cls._get_subnode(node, part)
        return cls._get_node(subnode, parts)

    @classmethod
    def _pop_next_part(cls, parts: PDeque[K]) -> tuple[K, PDeque[K]]:
        part = parts[0]
        parts = parts.popleft()
        return part, parts

    @classmethod
    def _read_node(cls, node: N) -> V:
        raise NotImplementedError

    @classmethod
    def _is_node_valid(cls, node: N) -> bool:
        raise NotImplementedError

    @classmethod
    def _get_subnode(cls, node: N, part: K) -> N:
        raise NotImplementedError


class PathAccessor(NodeAccessor[Path, str, bytes]):

    def keys(self, parts: Sequence[str]) -> Sequence[str]:
        subpath = Path(self.node, *parts)
        return [path.parts[0] for path in subpath.iterdir()]

    def len(self, parts: Sequence[str]) -> int:
        subpath = Path(self.node, *parts)
        return len(list(subpath.iterdir()))

    def read(self, parts: Sequence[str]) -> bytes:
        node = self._get_node(self.node, pdeque(parts))
        return self._read_node(node)

    @classmethod
    def _read_node(cls, node: Path) -> bytes:
        return node.read_bytes()

    @classmethod
    def _get_subnode(cls, node: Path, part: str) -> Path:
        subnode = node / part
        if not subnode.exists():
            raise KeyError
        return subnode


class SubscriptableAccessor(NodeAccessor[Union[Subscriptable[SK, SV], SV], SK, SV], Generic[SK, SV]):
    """Accessor for subscriptable content."""

    @classmethod
    def _get_subnode(cls, node: Union[Subscriptable[SK, SV], SV], part: SK) -> Union[Subscriptable[SK, SV], SV]:
        if not isinstance(node, Subscriptable) or not part in node:
            raise KeyError
        return node[part]


class CachedSubscriptableAccessor(SubscriptableAccessor[CSK, CSV], Generic[CSK, CSV]):

    _node_refs: dict[int, Union[Subscriptable[CSK, CSV], CSV]] = {}

    def __init__(self, node: Union[Subscriptable[CSK, CSV], CSV]):
        super().__init__(node)

        self._node_refs[id(node)] = node

    def read(self, parts: Sequence[CSK]) -> CSV:
        self._node_refs[id(self.node)] = self.node
        return self._read_cached(id(self.node), pdeque(parts))

    @classmethod
    @lru_cache
    def _read_cached(cls, node_id: int, parts: PDeque[CSK]) -> CSV:
        node: Union[Subscriptable[CSK, CSV], CSV] = cls._node_refs[node_id]
        node = cls._get_node(node, pdeque(parts))
        return cls._read_node(node)


class LookupAccessor(CachedSubscriptableAccessor[LookupKey, LookupValue]):

    def keys(self, parts: Sequence[LookupKey]) -> Sequence[LookupKey]:
        node = self._get_node(self.node, pdeque(parts))
        if isinstance(node, Mapping):
            return list(node.keys())
        if isinstance(node, list):
            return list(range(len(node)))
        raise AttributeError

    def len(self, parts: Sequence[LookupKey]) -> int:
        node = self._get_node(self.node, pdeque(parts))
        return len(node)

    @classmethod
    def _read_node(cls, node: LookupNode) -> LookupValue:
        return node
