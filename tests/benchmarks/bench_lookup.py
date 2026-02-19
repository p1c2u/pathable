"""Compatibility wrapper for deprecated tests.benchmarks command."""

import sys
import warnings
from pathlib import Path
from typing import Iterable

try:
    from pathable.benchmarks.bench_lookup import main as _main
except ModuleNotFoundError as exc:
    if exc.name != "pathable":
        raise
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pathable.benchmarks.bench_lookup import main as _main

_MESSAGE = (
    "tests.benchmarks.bench_lookup is deprecated and will be removed in a "
    "future release; use `pathable-bench run --impl pathable.LookupPath ...` "
    "or `python -m pathable.benchmarks.bench_lookup ...` instead."
)


def main(argv: Iterable[str] | None = None) -> int:
    warnings.warn(_MESSAGE, DeprecationWarning, stacklevel=2)
    return _main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
