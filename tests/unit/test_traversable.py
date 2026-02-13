from __future__ import annotations

from typing import Any
from typing import Sequence

from pathable.accessors import NodeAccessor


class KeysOnlyAccessor(NodeAccessor[dict[str, Any], str, Any]):
    def stat(self, parts: Sequence[str]) -> dict[str, Any] | None:
        return None

    def keys(self, parts: Sequence[str]) -> Sequence[str]:
        if parts:
            raise KeyError(parts[-1])
        return ["a", "b"]

    def len(self, parts: Sequence[str]) -> int:
        return len(self.keys(parts))


def test_is_traversable_falls_back_to_keys() -> None:
    a = KeysOnlyAccessor({})
    assert a.is_traversable(()) is True
    assert a.is_traversable(("missing",)) is False
