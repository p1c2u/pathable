"""Dictpath parsers module"""
from six import text_type


def parse_parts(parts, sep='/'):
    parsed = []
    it = reversed(parts)
    for part in it:
        if isinstance(part, int):
            parsed.append(part)
        if not part:
            continue
        if sep in part:
            for x in reversed(part.split(sep)):
                if x and x != '.':
                    parsed.append(x)
        else:
            if part and part != '.':
                parsed.append(part)
    parsed.reverse()
    return parsed


def parse_args(args, sep='/'):
    parts = []
    for a in args:
        if hasattr(a, 'parts'):
            parts += a.parts
        else:
            if isinstance(a, text_type):
                parts.append(a)
            elif isinstance(a, int):
                parts.append(a)
            else:
                raise TypeError(
                    "argument should be a text object or a Path "
                    "object returning str, not %r"
                    % type(a))
    return parse_parts(parts, sep)
