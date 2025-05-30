"""Pathable types module"""
from typing import Any
from typing import Union

from pathable.protocols import Subscriptable

LookupKey = Union[str, int]
LookupValue = Union["Lookup", Any]
Lookup = Subscriptable[LookupKey, LookupValue]
ParsePart = Union[str, int]
