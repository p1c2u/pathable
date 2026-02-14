"""Pathable parsers module"""

from __future__ import annotations

from collections.abc import Hashable
from typing import Sequence

SEPARATOR = "/"


def parse_parts(
    parts: Sequence[Hashable | None], sep: str = SEPARATOR
) -> list[Hashable]:
    """Parse (filter and split) path parts."""
    parsed: list[Hashable] = []
    append = parsed.append
    sep_check = sep
    for part in reversed(parts):
        if part is None:
            continue
        # Fast-path: int is common and never needs splitting/decoding.
        if isinstance(part, int):
            append(part)
            continue
        # Fast-path: str is most common.
        if isinstance(part, str):
            if part and part != ".":
                if sep_check in part:
                    for x in reversed(part.split(sep_check)):
                        if x and x != ".":
                            append(x)
                else:
                    append(part)
            continue
        # Fast-path: bytes, decode then treat as str.
        if isinstance(part, bytes):
            part = part.decode("ascii")
            if part and part != ".":
                if sep_check in part:
                    for x in reversed(part.split(sep_check)):
                        if x and x != ".":
                            append(x)
                else:
                    append(part)
            continue
        # Fallback: Hashable (covers e.g. tuple, custom keys).
        if isinstance(part, Hashable):
            append(part)
            continue
        raise TypeError(f"part must be Hashable or None; got {type(part)!r}")
    parsed.reverse()
    return parsed
