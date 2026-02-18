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
        match part:
            case None:
                continue
            # Fast-path: int is common and never needs splitting/decoding.
            case int():
                append(part)
            # Fast-path: str is most common.
            case str() as text_part:
                append_split(text_part)
            # Fast-path: bytes, decode then treat as str.
            case bytes() as binary_part:
                append_split(binary_part.decode("ascii"))
            # Fallback: Hashable (covers e.g. tuple, custom keys).
            case _ if isinstance(part, Hashable):
                append(part)
            case _:
                raise TypeError(
                    f"part must be Hashable or None; got {type(part)!r}"
                )
    parsed.reverse()
    return parsed
