# pathable

[![Package version](https://img.shields.io/pypi/v/pathable.svg)](https://pypi.org/project/pathable/)
[![Python versions](https://img.shields.io/pypi/pyversions/pathable.svg)](https://pypi.org/project/pathable/)
[![License](https://img.shields.io/pypi/l/pathable.svg)](https://pypi.org/project/pathable/)

## About

Pathable provides a small set of "path" objects for traversing hierarchical data (mappings, lists, and other subscriptable trees) using a familiar path-like syntax.

It’s especially handy when you want to:

* express deep lookups as a single object (and pass it around)
* build paths incrementally (`p / "a" / 0 / "b"`)
* safely probe (`exists()`, `get(...)`) or strictly require segments (`//`)

## Key features

* Intuitive path-based navigation for nested data (e.g., dicts/lists)
* Pluggable accessor layer for custom backends
* Pythonic, chainable API for concise and readable code
* Per-instance cached lookup accessor for repeated reads of the same tree

## Quickstart

```python
from pathable import LookupPath

data = {
    "parts": {
        "part1": {"name": "Part One"},
        "part2": {"name": "Part Two"},
    }
}

root = LookupPath.from_lookup(data)

name = (root / "parts" / "part2" / "name").read_value()
assert name == "Part Two"
```

## Usage

```python
from pathable import LookupPath

data = {
    "parts": {
        "part1": {"name": "Part One"},
        "part2": {"name": "Part Two"},
    }
}

p = LookupPath.from_lookup(data)

# Concatenate path segments with /
parts = p / "parts"

# Check membership (mapping keys or list indexes)
assert "part2" in parts

# Read a value
assert (parts / "part2" / "name").read_value() == "Part Two"

# Iterate children as paths
for child in parts:
    print(child, child.read_value())

# Work with keys/items
print(list(parts.keys()))
print({k: v.read_value() for k, v in parts.items()})

# Safe access
print(parts.get("missing", default=None))

# Strict access (raises KeyError if missing)
must_exist = parts // "part2"

# "Open" yields the current value as a context manager
with parts.open() as parts_value:
    assert isinstance(parts_value, dict)

# Optional metadata
print(parts.stat())
```

## Filesystem example

Pathable can also traverse the filesystem via an accessor.

```python
from pathlib import Path

from pathable import FilesystemPath

root_dir = Path(".")
p = FilesystemPath.from_path(root_dir)

readme = p / "README.md"
if readme.exists():
    content = readme.read_value()  # bytes
    print(content[:100])
```

## Core concepts

* `BasePath` is a pure path (segments + separator) with `/` joining.
* `AccessorPath` is a `BasePath` bound to a `NodeAccessor`, enabling `read_value()`, `exists()`, `keys()`, iteration, etc.
* `FilesystemPath` is an `AccessorPath` specialized for filesystem objects.
* `LookupPath` is an `AccessorPath` specialized for mapping/list lookups.

Notes on parsing:

* A segment like `"a/b"` is split into parts using the separator.
* `None` segments are ignored.
* `"."` segments are ignored (relative no-op).
* Operations like `relative_to()` and `is_relative_to()` also respect the instance separator.

Equality and ordering:

* `BasePath` equality, hashing, and ordering are all based on both `separator` and `parts`.
* Ordering is separator-sensitive and deterministic, even when parts mix types (e.g. ints and strings).
* Path parts are type-sensitive (`0` is not equal to `"0"`).

## Installation

Recommended way (via pip):

``` console
pip install pathable
```

Alternatively you can download the code and install from the repository:

``` console
pip install -e git+https://github.com/p1c2u/pathable.git#egg=pathable
```

