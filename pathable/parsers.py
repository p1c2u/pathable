"""Pathable parsers module"""

from collections.abc import Hashable
from typing import Sequence

SEPARATOR = "/"


def parse_parts(
    parts: Sequence[Hashable | None], sep: str = SEPARATOR
) -> list[Hashable]:
    """Parse (filter and split) path parts."""
    parsed: list[Hashable] = []
    it = reversed(parts)
    for part in it:
        if part is None:
            continue
        if isinstance(part, bytes):
            part = part.decode("ascii")
        if isinstance(part, str):
            if sep in part:
                for x in reversed(part.split(sep)):
                    if x and x != ".":
                        parsed.append(x)
            else:
                if part and part != ".":
                    parsed.append(part)
            continue
        if isinstance(part, Hashable):
            parsed.append(part)
            continue
        raise TypeError(
            "part must be Hashable or None; got %r" % (type(part),)
        )
    parsed.reverse()
    return parsed
