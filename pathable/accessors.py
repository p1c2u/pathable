"""Pathable accessors module"""
from contextlib import contextmanager


class LookupAccessor(object):
    """Accessor for object that supports __getitem__ lookups"""

    def __init__(self, lookup):
        self.lookup = lookup

    def stat(self, parts):
        return NotImplementedError

    def keys(self, parts):
        with self.open(parts) as d:
            return d.keys()

    def len(self, parts):
        with self.open(parts) as d:
            return len(d)

    @contextmanager
    def open(self, parts):
        content = self.lookup
        for part in parts:
            content = content[part]
        try:
            yield content
        finally:
            pass
