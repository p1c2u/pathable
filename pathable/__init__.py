# -*- coding: utf-8 -*-
"""Pathable module"""
from pathable.paths import (
    BasePath, AccessorPath, LookupPath,
    LookupPath as DictPath,
    LookupPath as ListPath,
)

__author__ = 'Artur Maciag'
__email__ = 'maciag.artur@gmail.com'
__version__ = '0.3.0'
__url__ = 'https://github.com/p1c2u/pathable'
__license__ = 'Apache License, Version 2.0'

__all__ = [
    'BasePath', 'AccessorPath', 'LookupPath',
    'DictPath', 'ListPath',
]
