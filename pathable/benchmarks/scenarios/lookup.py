"""Benchmarks for AccessorPath lookup-style operations."""

from typing import Any

from pathable.accessors import LookupAccessor
from pathable.benchmarks.core import BenchmarkResult
from pathable.benchmarks.core import run_benchmark
from pathable.paths import AccessorPath


def _build_deep_tree(depth: int) -> dict[str, Any]:
    node: dict[str, Any] = {"value": 1}
    for i in range(depth - 1, -1, -1):
        node = {f"k{i}": node}
    return node


def _deep_keys(depth: int) -> tuple[str, ...]:
    return tuple(f"k{i}" for i in range(depth))


def _make_deep_path(root: AccessorPath[Any, Any, Any], depth: int) -> Any:
    p: Any = root
    for k in _deep_keys(depth):
        p = p / k
    return p


def _build_mapping(size: int) -> dict[str, int]:
    return {f"k{i}": i for i in range(size)}


def _from_lookup(
    impl: type[AccessorPath[Any, Any, Any]], lookup: Any, *parts: Any
) -> AccessorPath[Any, Any, Any]:
    ctor = getattr(impl, "from_lookup", None)
    if ctor is None or not callable(ctor):
        raise TypeError(
            f"{impl.__module__}.{impl.__qualname__} does not provide from_lookup()"
        )
    path = ctor(lookup, *parts)
    if not isinstance(path, AccessorPath):
        raise TypeError("from_lookup() must return AccessorPath instance")
    return path


def _benchmark_lookup(
    impl: type[AccessorPath[Any, Any, Any]],
    *,
    quick: bool,
    repeats: int,
    warmup_loops: int,
) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    depth = 25 if not quick else 10
    loops_hit = 200_000 if not quick else 20_000
    loops_miss = 80_000 if not quick else 10_000

    data = _build_deep_tree(depth)
    root = _from_lookup(impl, data)
    deep = _make_deep_path(root, depth)

    results.append(
        run_benchmark(
            f"lookup.read_value.cache_hit.depth{depth}",
            deep.read_value,
            loops=loops_hit,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    leaf_parent = _from_lookup(
        impl,
        {"root": {"branch": {"leaf": "value"}}},
        "root",
        "branch",
    )

    def getitem_leaf(_p: AccessorPath[Any, Any, Any] = leaf_parent) -> None:
        _ = _p["leaf"]

    loops_getitem_leaf = 200_000 if not quick else 20_000
    results.append(
        run_benchmark(
            "lookup.getitem.leaf",
            getitem_leaf,
            loops=loops_getitem_leaf,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    branch_parent = _from_lookup(
        impl,
        {"root": {"branch": {"child": {"x": 1}}}},
        "root",
        "branch",
    )

    def getitem_branch(
        _p: AccessorPath[Any, Any, Any] = branch_parent,
    ) -> None:
        _ = _p["child"]

    loops_getitem_branch = 200_000 if not quick else 20_000
    results.append(
        run_benchmark(
            "lookup.getitem.branch",
            getitem_branch,
            loops=loops_getitem_branch,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    deep_accessor = deep.accessor
    if not isinstance(deep_accessor, LookupAccessor):
        raise TypeError(
            "lookup scenarios require LookupAccessor-backed implementation"
        )
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

    data2 = {
        "a": _build_deep_tree(depth),
        "x": _build_deep_tree(depth),
    }
    root2 = _from_lookup(impl, data2)
    a_path = _make_deep_path(root2 / "a", depth)
    x_path = _make_deep_path(root2 / "x", depth)

    root2_accessor = root2.accessor
    if not isinstance(root2_accessor, LookupAccessor):
        raise TypeError(
            "lookup scenarios require LookupAccessor-backed implementation"
        )
    root2_accessor.enable_cache(maxsize=1)

    toggle = {"i": 0}

    def read_alternating() -> None:
        if toggle["i"] & 1:
            x_path.read_value()
        else:
            a_path.read_value()
        toggle["i"] += 1

    loops_eviction = 120_000 if not quick else 15_000
    results.append(
        run_benchmark(
            f"lookup.read_value.eviction_alternate.maxsize1.depth{depth}",
            read_alternating,
            loops=loops_eviction,
            repeats=repeats,
            warmup_loops=warmup_loops,
        )
    )

    sizes = [10, 1_000, 50_000] if not quick else [10, 1_000]
    for size in sizes:
        mapping = _build_mapping(size)
        p = _from_lookup(impl, {"root": mapping}) / "root"

        loops_keys = 5_000 if size <= 1_000 else 200
        if quick:
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

        probe_key = f"k{size - 1}" if size else "k0"
        loops_contains = 20_000 if size <= 1_000 else 500
        if quick:
            loops_contains = min(loops_contains, 2_000)

        def contains_probe(
            _p: AccessorPath[Any, Any, Any] = p,
            _key: str = probe_key,
        ) -> None:
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

        loops_floordiv = 20_000 if size <= 1_000 else 500
        if quick:
            loops_floordiv = min(loops_floordiv, 2_000)

        def floordiv_probe(
            _p: AccessorPath[Any, Any, Any] = p,
            _key: str = probe_key,
        ) -> None:
            _ = _p // _key

        results.append(
            run_benchmark(
                f"lookup.floordiv.mapping.size{size}",
                floordiv_probe,
                loops=loops_floordiv,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

        missing_key = "missing"

        def floordiv_missing_probe(
            _p: AccessorPath[Any, Any, Any] = p,
            _key: str = missing_key,
        ) -> None:
            try:
                _ = _p // _key
            except KeyError:
                return

        results.append(
            run_benchmark(
                f"lookup.floordiv_missing.mapping.size{size}",
                floordiv_missing_probe,
                loops=loops_floordiv,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

        loops_iter = 500 if size <= 1_000 else 3
        if quick:
            loops_iter = min(loops_iter, 50)

        def iter_children(_p: AccessorPath[Any, Any, Any] = p) -> None:
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

    return results


def run_lookup_scenarios(
    impl: type[AccessorPath[Any, Any, Any]],
    *,
    quick: bool,
    repeats: int,
    warmup_loops: int,
) -> list[BenchmarkResult]:
    return _benchmark_lookup(
        impl,
        quick=quick,
        repeats=repeats,
        warmup_loops=warmup_loops,
    )
