# pathable

<a href="https://pypi.python.org/pypi/pathable" target="_blank">
    <img src="https://img.shields.io/pypi/v/pathable.svg" alt="Package version">
</a>
<a href="https://travis-ci.org/p1c2u/pathable" target="_blank">
    <img src="https://travis-ci.org/p1c2u/pathable.svg?branch=master" alt="Continuous Integration">
</a>
<a href="https://codecov.io/github/p1c2u/pathable?branch=master" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/p1c2u/pathable/master.svg?style=flat" alt="Tests coverage">
</a>
<a href="https://pypi.python.org/pypi/pathable" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/pathable.svg" alt="Python versions">
</a>
<a href="https://pypi.python.org/pypi/pathable" target="_blank">
    <img src="https://img.shields.io/pypi/format/pathable.svg" alt="Package format">
</a>
<a href="https://pypi.python.org/pypi/pathable" target="_blank">
    <img src="https://img.shields.io/pypi/status/pathable.svg" alt="Development status">
</a>

## About

Pathable provides a flexible, object-oriented interface for traversing and manipulating hierarchical data structures (such as lists or dictionaries) using path-like syntax. It enables intuitive navigation, access, and modification of nested resources in Python.

## Key features

* Intuitive path-based navigation for nested data (e.g., lists, dicts)
* Pluggable accessor layer for custom data sources or backends
* Pythonic, chainable API for concise and readable code

## Usage

```python
from pathable import DictPath

d = {
    "parts": {
        "part1": {
            "name": "Part One",
        },
        "part2": {
            "name": "Part Two",
        },
    },
}

dp = DictPath(d)

# Concatenate paths with /
parts = dp / "parts"

# Stat path keys
"part2" in parts

# Open path dict
with parts.open() as parts_dict:
    print(parts_dict)
```

## Installation

Recommended way (via pip):

``` console
pip install pathable
```

Alternatively you can download the code and install from the repository:

``` console
pip install -e git+https://github.com/p1c2u/pathable.git#egg=pathable
```

