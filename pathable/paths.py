"""Pathable paths module"""
import warnings
from collections.abc import Hashable
from collections.abc import Iterator
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any
from typing import Sequence
from typing import Type
from typing import TypeVar
from typing import Union

from pathable.accessors import BaseAccessor
from pathable.accessors import LookupAccessor
from pathable.dataclasses import BasePathData
from pathable.parsers import SEPARATOR
from pathable.parsers import parse_args
from pathable.types import Lookup

TBasePath = TypeVar("TBasePath", bound="BasePath")
TAccessorPath = TypeVar("TAccessorPath", bound="AccessorPath")
TLookupPath = TypeVar("TLookupPath", bound="LookupPath")


class BasePath(BasePathData):
    """Base path."""

    def __init__(self, *args: Any, **kwargs: Any):
        parts = parse_args(list(args))
        separator = kwargs.pop("separator", SEPARATOR)
        super().__init__(parts, separator=separator)

        self._cparts_cached: Union[tuple[str, ...], None] = None

    @classmethod
    def _from_parts(
        cls: Type[TBasePath], args: Sequence[Any], separator: str = SEPARATOR
    ) -> TBasePath:
        self = cls(separator=separator)
        self.parts = parse_args(args)
        return self

    @classmethod
    def _from_parsed_parts(
        cls: Type[TBasePath], parts: tuple[Hashable, ...], separator: str = SEPARATOR
    ) -> TBasePath:
        self = cls(separator=separator)
        self.parts = parts
        return self

    @property
    def _cparts(self) -> tuple[str, ...]:
        # Cached casefolded parts, for hashing and comparison
        if self._cparts_cached is None:
            self._cparts_cached = self._get_cparts()
        return self._cparts_cached

    def _get_cparts(self) -> tuple[str, ...]:
        return tuple(str(p) for p in self.parts)

    def _make_child(self: TBasePath, args: list[Any]) -> TBasePath:
        parts = parse_args(args, self.separator)
        parts_joined = self.parts + parts
        return self._from_parsed_parts(parts_joined, self.separator)

    def _make_child_relpath(self: TBasePath, part: Hashable) -> TBasePath:
        # This is an optimization used for dir walking.  `part` must be
        # a single part relative to this path.
        parts = self.parts + (part, )
        return self._from_parsed_parts(parts, self.separator)

    def __str__(self) -> str:
        return self.separator.join(self._cparts)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self)!r})"

    def __hash__(self) -> int:
        return hash(tuple(self._cparts))

    def __truediv__(self: TBasePath, key: Any) -> TBasePath:
        try:
            return self._make_child(
                [
                    key,
                ]
            )
        except TypeError:
            return NotImplemented

    def __rtruediv__(self: TBasePath, key: Hashable) -> TBasePath:
        try:
            return self._from_parts((key, ) + self.parts)
        except TypeError:
            return NotImplemented

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BasePath):
            return NotImplemented
        return self._cparts == other._cparts

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, BasePath):
            return NotImplemented
        return self._cparts < other._cparts

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, BasePath):
            return NotImplemented
        return self._cparts <= other._cparts

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, BasePath):
            return NotImplemented
        return self._cparts > other._cparts

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, BasePath):
            return NotImplemented
        return self._cparts >= other._cparts


class AccessorPath(BasePath):
    """Path for object that can be read by accessor."""

    def __init__(self, accessor: BaseAccessor, *args: Any, **kwargs: Any):
        separator = kwargs.pop("separator", SEPARATOR)
        super().__init__(*args, separator=separator)
        self.accessor = accessor

        self._content_cached: Any = None

    @classmethod
    def _from_parsed_parts(
        cls: Type[TAccessorPath],
        parts: tuple[Hashable, ...],
        separator: str = SEPARATOR,
        accessor: Union[BaseAccessor, None] = None,
    ) -> TAccessorPath:
        if accessor is None:
            raise ValueError("accessor must be provided")
        self = cls(accessor, separator=separator)
        self.parts = parts
        return self

    def _make_child(self: TAccessorPath, args: list[Any]) -> TAccessorPath:
        parts = parse_args(args, self.separator)
        parts_joined = self.parts + parts
        return self._from_parsed_parts(
            parts_joined, separator=self.separator, accessor=self.accessor,
        )

    def _make_child_relpath(
        self: TAccessorPath, part: Hashable
    ) -> TAccessorPath:
        # This is an optimization used for dir walking.  `part` must be
        # a single part relative to this path.
        parts = self.parts + (part, )
        return self._from_parsed_parts(
            parts, separator=self.separator, accessor=self.accessor,
        )

    def __iter__(self: TAccessorPath) -> Iterator[TAccessorPath]:
        for key in self.accessor.keys(self.parts):
            yield self._make_child_relpath(key)

    def __getitem__(self, key: Hashable) -> Any:
        with self.open() as d:
            return d[key]

    def __contains__(self, key: Hashable) -> bool:
        return key in self.accessor.keys(self.parts)

    def __len__(self) -> int:
        return self.accessor.len(self.parts)

    def keys(self) -> Any:
        return self.accessor.keys(self.parts)

    def getkey(self, key: Hashable, default: Any = None) -> Any:
        """Return the value for key if key is in the path, else default."""
        warnings.warn(
            "'getkey' method is deprecated. Use 'key not in path' and 'path.read_value' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if key not in self:
            raise default
        path = self / key
        return path.read_value()

    def iter(self: TAccessorPath) -> Iterator[TAccessorPath]:
        """Iterate over all child paths."""
        warnings.warn(
            "'iter' method is deprecated. Use 'iter(path)' instead.",
            DeprecationWarning,
        )
        return iter(self)

    def iteritems(self: TAccessorPath) -> Iterator[tuple[Any, TAccessorPath]]:
        """Return path's items."""
        warnings.warn(
            "'iteritems' method is deprecated. Use 'items' instead.",
            DeprecationWarning,
        )
        return self.items()

    def items(self: TAccessorPath) -> Iterator[tuple[Any, TAccessorPath]]:
        """Return path's items."""
        for key in self.accessor.keys(self.parts):
            yield key, self._make_child_relpath(key)

    def content(self) -> Any:
        warnings.warn(
            "'content' method is deprecated.",
            DeprecationWarning,
        )
        with self.open() as d:
            return d

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Return the child path for key if key is in the path, else default."""
        warnings.warn(
            "'get' method is deprecated. Use 'key in path' and 'path / key' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if key in self:
            return self / key
        return default

    @contextmanager
    def open(self) -> Any:
        """Open the path."""
        with self.accessor.open(self.parts) as content:
            yield content

    def read_value(self) -> Any:
        """Return the path's value."""
        with self.open() as d:
            return d


class LookupPath(AccessorPath):
    """Path for object that supports __getitem__ lookups."""

    @classmethod
    def _from_lookup(
        cls: Type[TLookupPath],
        lookup: Lookup,
        *args: Any,
        **kwargs: Any,
    ) -> TLookupPath:
        accessor = LookupAccessor(lookup)
        return cls(accessor, *args, **kwargs)
