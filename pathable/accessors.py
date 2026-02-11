"""Pathable accessors module"""
from collections.abc import Hashable
from collections.abc import Mapping
from collections.abc import Sequence
from pathlib import Path
import sys
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

    def stat(self, parts: Sequence[K]) -> Union[dict[str, Any], None]:
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

    def stat(self, parts: Sequence[str]) -> Union[dict[str, Any], None]:
        subpath = self.node.joinpath(*parts)
        try:
            # Avoid following symlinks (Python 3.10+)
            if sys.version_info >= (3, 10):
                stat = subpath.stat(follow_symlinks=False)
            else:
                stat = subpath.lstat()
        except OSError:
            return None
        return {
            key: getattr(stat, key)
            for key in dir(stat)
            if key.startswith("st_")
        }

    def keys(self, parts: Sequence[str]) -> Sequence[str]:
        subpath = Path(self.node, *parts)
        return [path.name for path in subpath.iterdir()]

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
        if not isinstance(node, Subscriptable):
            raise KeyError
        return node[part]


class CachedSubscriptableAccessor(SubscriptableAccessor[CSK, CSV], Generic[CSK, CSV]):
    def __init__(self, node: Union[Subscriptable[CSK, CSV], CSV]):
        super().__init__(node)

        # Per-instance cache: avoids global strong references and id-reuse hazards.
        self._cache: dict[tuple[CSK, ...], CSV] = {}

    def read(self, parts: Sequence[CSK]) -> CSV:
        key = tuple(parts)
        try:
            return self._cache[key]
        except KeyError:
            node = self._get_node(self.node, pdeque(parts))
            value = self._read_node(node)
            self._cache[key] = value
            return value


class LookupAccessor(CachedSubscriptableAccessor[LookupKey, LookupValue]):

    def stat(self, parts: Sequence[LookupKey]) -> Union[dict[str, Any], None]:
        try:
            node = self._get_node(self.node, pdeque(parts))
        except KeyError:
            return None

        if isinstance(node, Mapping):
            return {
                'type': 'mapping',
                'length': len(node),
            }
        if isinstance(node, list):
            return {
                'type': 'list',
                'length': len(node),
            }
        try:
            length = len(node)
        except TypeError:
            length = None

        return {
            'type': type(node),
            'length': length,
        }

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
