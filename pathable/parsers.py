"""Pathable parsers module"""

from collections.abc import Hashable
from typing import Sequence

SEPARATOR = "/"


def parse_parts(
    parts: Sequence[Hashable | None], sep: str = SEPARATOR
) -> list[Hashable]:
    """Parse (filter and split) path parts."""

    def append_split(part: str) -> None:
        if not part or part == ".":
            return
        if sep_check in part:
            for split_part in reversed(part.split(sep_check)):
                if split_part and split_part != ".":
                    append(split_part)
            return
        append(part)

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
            append_split(part)
            continue
        # Fast-path: bytes, decode then treat as str.
        if isinstance(part, bytes):
            append_split(part.decode("ascii"))
            continue
        # Fallback: Hashable (covers e.g. tuple, custom keys).
        if isinstance(part, Hashable):
            append(part)
            continue
        raise TypeError(f"part must be Hashable or None; got {type(part)!r}")
    parsed.reverse()
    return parsed
