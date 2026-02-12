"""Benchmarks for LookupPath / LookupAccessor hot paths.

These benchmarks avoid filesystem I/O (too noisy for CI) and focus on:
- traversal cost (cache disabled)
- cache hit speed
- LRU eviction patterns
- keys/contains/iter overhead on large mappings
"""

import argparse
from typing import Any
from typing import Iterable

from pathable.accessors import LookupAccessor
from pathable.paths import LookupPath

try:
    # Prefer module execution: `python -m tests.benchmarks.bench_lookup ...`
    from .bench_utils import BenchmarkResult
    from .bench_utils import add_common_args
    from .bench_utils import results_to_json
    from .bench_utils import run_benchmark
    from .bench_utils import write_json
except ImportError:  # pragma: no cover
    # Allow direct execution: `python tests/benchmarks/bench_lookup.py ...`
    from bench_utils import BenchmarkResult  # type: ignore[no-redef]
    from bench_utils import add_common_args  # type: ignore[no-redef]
    from bench_utils import results_to_json  # type: ignore[no-redef]
    from bench_utils import run_benchmark  # type: ignore[no-redef]
    from bench_utils import write_json  # type: ignore[no-redef]


def _build_deep_tree(depth: int) -> dict[str, Any]:
    node: dict[str, Any] = {"value": 1}
    for i in range(depth - 1, -1, -1):
        node = {f"k{i}": node}
    return node


def _deep_keys(depth: int) -> tuple[str, ...]:
    return tuple(f"k{i}" for i in range(depth))


def _make_deep_path(root: LookupPath, depth: int) -> LookupPath:
    p = root
    for k in _deep_keys(depth):
        p = p / k
    return p


def _build_mapping(size: int) -> dict[str, int]:
    return {f"k{i}": i for i in range(size)}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    args = parser.parse_args(list(argv) if argv is not None else None)

    repeats: int = args.repeats
    warmup_loops: int = args.warmup_loops

    results: list[BenchmarkResult] = []

    # --- Lookup read benchmarks ---
    depth = 25 if not args.quick else 10
    loops_hit = 200_000 if not args.quick else 20_000
    loops_miss = 80_000 if not args.quick else 10_000

    data = _build_deep_tree(depth)
    root = LookupPath.from_lookup(data)
    deep = _make_deep_path(root, depth)

    # Cache hit: repeated reads of the same path.
    results.append(
        run_benchmark(
            f"lookup.read_value.cache_hit.depth{depth}",
            deep.read_value,
            loops=loops_hit,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    # Cache miss cost: disable cache and repeatedly read.
    deep_accessor = deep.accessor
    if not isinstance(deep_accessor, LookupAccessor):
        raise TypeError("Expected LookupPath.accessor to be LookupAccessor")
    deep_accessor.disable_cache()
    results.append(
        run_benchmark(
            f"lookup.read_value.cache_disabled.depth{depth}",
            deep.read_value,
            loops=loops_miss,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    # LRU eviction: alternate two distinct deep paths with maxsize=1.
    data2 = {
        "a": _build_deep_tree(depth),
        "x": _build_deep_tree(depth),
    }
    root2 = LookupPath.from_lookup(data2)
    a_path = _make_deep_path(root2 / "a", depth)
    x_path = _make_deep_path(root2 / "x", depth)

    root2_accessor = root2.accessor
    if not isinstance(root2_accessor, LookupAccessor):
        raise TypeError("Expected LookupPath.accessor to be LookupAccessor")
    root2_accessor.enable_cache(maxsize=1)

    toggle = {"i": 0}

    def read_alternating() -> None:
        if toggle["i"] & 1:
            x_path.read_value()
        else:
            a_path.read_value()
        toggle["i"] += 1

    loops_eviction = 120_000 if not args.quick else 15_000
    results.append(
        run_benchmark(
            f"lookup.read_value.eviction_alternate.maxsize1.depth{depth}",
            read_alternating,
            loops=loops_eviction,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    # --- Large mapping operations ---
    sizes = [10, 1_000, 50_000] if not args.quick else [10, 1_000]
    for size in sizes:
        mapping = _build_mapping(size)
        p = LookupPath.from_lookup({"root": mapping}) / "root"

        # keys() materializes a list in LookupAccessor.keys for mappings.
        loops_keys = 5_000 if size <= 1_000 else 200
        if args.quick:
            loops_keys = min(loops_keys, 500)

        results.append(
            run_benchmark(
                f"lookup.keys.mapping.size{size}",
                p.keys,
                loops=loops_keys,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

        # contains: AccessorPath.__contains__ calls keys() then `in`.
        probe_key = f"k{size - 1}" if size else "k0"
        loops_contains = 20_000 if size <= 1_000 else 500
        if args.quick:
            loops_contains = min(loops_contains, 2_000)

        def contains_probe(_p: LookupPath = p, _key: str = probe_key) -> None:
            _ = _key in _p

        results.append(
            run_benchmark(
                f"lookup.contains.mapping.size{size}",
                contains_probe,
                loops=loops_contains,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

        # iterating children: should call keys() once and yield child paths.
        loops_iter = 500 if size <= 1_000 else 3
        if args.quick:
            loops_iter = min(loops_iter, 50)

        def iter_children(_p: LookupPath = p) -> None:
            for _ in _p:
                pass

        results.append(
            run_benchmark(
                f"lookup.iter_children.mapping.size{size}",
                iter_children,
                loops=loops_iter,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

    payload = results_to_json(results=results)
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
