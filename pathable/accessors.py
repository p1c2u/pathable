"""Pathable accessors module"""

import sys
from collections import OrderedDict
from collections.abc import Hashable
from collections.abc import Mapping
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from typing import Generic
from typing import Optional
from typing import TypeVar
from typing import Union

from pathable.protocols import Subscriptable
from pathable.types import LookupKey
from pathable.types import LookupNode
from pathable.types import LookupValue

K = TypeVar("K", bound=Hashable, contravariant=True)
V = TypeVar("V", covariant=True)
N = TypeVar("N")
SK = TypeVar("SK", bound=Hashable, contravariant=True)
SV = TypeVar("SV", covariant=True)
CSK = TypeVar("CSK", bound=Hashable, contravariant=True)
CSV = TypeVar("CSV", covariant=True)


class NodeAccessor(Generic[N, K, V]):
    """Node accessor."""

    def __init__(self, node: N):
        self._node = node

    @property
    def node(self) -> N:
        return self._node

    def __eq__(self, other: object) -> Any:
        if not isinstance(other, NodeAccessor):
            return NotImplemented
        return self.node == other.node

    def stat(self, parts: Sequence[K]) -> Union[dict[str, Any], None]:
        raise NotImplementedError

    def keys(self, parts: Sequence[K]) -> Sequence[K]:
        """Return the keys of the node at `parts` if it is traversable, or raise `KeyError` if not.

        This performs a segment-by-segment traversal and raises `KeyError` with the failing segment if any part is missing or non-traversable.
        """
        raise NotImplementedError

    def len(self, parts: Sequence[K]) -> int:
        raise NotImplementedError

    def read(self, parts: Sequence[K]) -> V:
        node = self._get_node(self.node, parts)
        return self._read_node(node)

    def validate(self, parts: Sequence[K]) -> None:
        """Validate that the node at `parts` exists.

        This performs a traversal only and raises `KeyError` (with the failing
        part when available) if the path is missing or non-traversable.
        """
        self._get_node(self.node, parts)

    @classmethod
    def _get_node(cls, node: N, parts: Sequence[K]) -> N:
        current = node
        for part in parts:
            current = cls._get_subnode(current, part)
        return current

    @classmethod
    def _read_node(cls, node: N) -> V:
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
        # Traverse using `_get_node()` so missing intermediate segments are
        # reported by `_get_subnode()` with the first failing part.
        subpath = self._get_node(self.node, parts)
        try:
            return [path.name for path in subpath.iterdir()]
        except (FileNotFoundError, NotADirectoryError) as exc:
            if parts:
                raise KeyError(parts[-1]) from exc
            raise KeyError from exc

    def len(self, parts: Sequence[str]) -> int:
        # Traverse using `_get_node()` so missing intermediate segments are
        # reported by `_get_subnode()` with the first failing part.
        subpath = self._get_node(self.node, parts)
        try:
            return sum(1 for _ in subpath.iterdir())
        except (FileNotFoundError, NotADirectoryError) as exc:
            if parts:
                raise KeyError(parts[-1]) from exc
            raise KeyError from exc

    def read(self, parts: Sequence[str]) -> bytes:
        node = self._get_node(self.node, parts)
        return self._read_node(node)

    @classmethod
    def _read_node(cls, node: Path) -> bytes:
        return node.read_bytes()

    @classmethod
    def _get_subnode(cls, node: Path, part: str) -> Path:
        subnode = node / part
        if not subnode.exists():
            raise KeyError(part)
        return subnode


class SubscriptableAccessor(
    NodeAccessor[Union[Subscriptable[SK, SV], SV], SK, SV], Generic[SK, SV]
):
    """Accessor for subscriptable content."""

    @classmethod
    def _get_subnode(
        cls, node: Union[Subscriptable[SK, SV], SV], part: SK
    ) -> Union[Subscriptable[SK, SV], SV]:
        if not isinstance(node, Subscriptable):
            raise KeyError(part)
        try:
            return node[part]
        except (KeyError, IndexError, TypeError) as exc:
            raise KeyError(part) from exc


class CachedSubscriptableAccessor(
    SubscriptableAccessor[CSK, CSV], Generic[CSK, CSV]
):
    def __init__(self, node: Union[Subscriptable[CSK, CSV], CSV]):
        super().__init__(node)

        # Per-instance cache: avoids global strong references and id-reuse hazards.
        # Default maxsize matches functools.lru_cache default (128).
        self._cache_enabled = True
        self._cache_maxsize: Optional[int] = 128
        self._cache: OrderedDict[tuple[CSK, ...], CSV] = OrderedDict()

    def clear_cache(self) -> None:
        """Clear any cached reads for this accessor instance."""
        self._cache.clear()

    def disable_cache(self) -> None:
        """Disable caching for this accessor instance."""
        self._cache_enabled = False
        self._cache.clear()

    def enable_cache(self, *, maxsize: Optional[int] = 128) -> None:
        """Enable caching for this accessor instance.

        Args:
            maxsize: Maximum number of distinct paths to cache.
                - 128 by default (matches functools.lru_cache)
                - None for unbounded
                - 0 to disable caching
        """
        self._cache_enabled = True
        self._cache_maxsize = maxsize
        self._cache.clear()

    def read(self, parts: Sequence[CSK]) -> CSV:
        key = tuple(parts)
        if (not self._cache_enabled) or self._cache_maxsize == 0:
            node = self._get_node(self.node, parts)
            return self._read_node(node)

        try:
            value = self._cache[key]
        except KeyError:
            node = self._get_node(self.node, parts)
            value = self._read_node(node)
            self._cache[key] = value
        else:
            # Mark as recently used.
            self._cache.move_to_end(key)
            return value

        # Enforce max size (LRU eviction).
        if self._cache_maxsize is not None:
            while len(self._cache) > self._cache_maxsize:
                self._cache.popitem(last=False)

        return value


class LookupAccessor(CachedSubscriptableAccessor[LookupKey, LookupValue]):

    def stat(self, parts: Sequence[LookupKey]) -> Union[dict[str, Any], None]:
        try:
            node = self._get_node(self.node, parts)
        except KeyError:
            return None

        if isinstance(node, Mapping):
            return {
                "type": "mapping",
                "length": len(node),
            }
        if isinstance(node, list):
            return {
                "type": "list",
                "length": len(node),
            }
        try:
            length = len(node)
        except TypeError:
            length = None

        return {
            "type": type(node),
            "length": length,
        }

    def keys(self, parts: Sequence[LookupKey]) -> Sequence[LookupKey]:
        node = self._get_node(self.node, parts)
        if isinstance(node, Mapping):
            return list(node.keys())
        if isinstance(node, list):
            return list(range(len(node)))
        return []

    def len(self, parts: Sequence[LookupKey]) -> int:
        node = self._get_node(self.node, parts)
        # Define length as the number of child paths (consistent with keys()).
        if isinstance(node, Mapping):
            return len(node)
        if isinstance(node, list):
            return len(node)
        return 0

    @classmethod
    def _read_node(cls, node: LookupNode) -> LookupValue:
        return node
