"""Pathable types module"""
from typing import Any
from typing import Union

from pathable.protocols import Subscriptable

LookupKey = Union[str, int]
LookupValue = Any
LookupNode = Union[Subscriptable[LookupKey, LookupValue], LookupValue]
ParsePart = Union[str, int]
