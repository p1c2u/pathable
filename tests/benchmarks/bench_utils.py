"""Compatibility exports for deprecated benchmark utility module."""

import sys
import warnings
from pathlib import Path

try:
    from pathable.benchmarks.core import BenchmarkResult
    from pathable.benchmarks.core import add_common_args
    from pathable.benchmarks.core import default_meta
    from pathable.benchmarks.core import results_to_json
    from pathable.benchmarks.core import run_benchmark
    from pathable.benchmarks.core import write_json
except ModuleNotFoundError as exc:
    if exc.name != "pathable":
        raise
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from pathable.benchmarks.core import BenchmarkResult
    from pathable.benchmarks.core import add_common_args
    from pathable.benchmarks.core import default_meta
    from pathable.benchmarks.core import results_to_json
    from pathable.benchmarks.core import run_benchmark
    from pathable.benchmarks.core import write_json

warnings.warn(
    "tests.benchmarks.bench_utils is deprecated and will be removed in a "
    "future release; use pathable.benchmarks.core instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "BenchmarkResult",
    "add_common_args",
    "default_meta",
    "results_to_json",
    "run_benchmark",
    "write_json",
]
