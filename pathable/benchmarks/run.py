"""Benchmark runner orchestration."""

from typing import Any

from pathable.benchmarks.core import BenchmarkResult
from pathable.benchmarks.core import default_meta
from pathable.benchmarks.core import results_to_json
from pathable.benchmarks.registry import resolve_impl
from pathable.benchmarks.scenarios.lookup import run_lookup_scenarios
from pathable.benchmarks.scenarios.parse import run_parse_scenarios
from pathable.paths import AccessorPath


def run_all(
    *,
    impl_target: str,
    quick: bool,
    repeats: int,
    warmup_loops: int,
    scenarios: tuple[str, ...] = ("parse", "lookup"),
) -> dict[str, Any]:
    impl = resolve_impl(impl_target)

    results: list[BenchmarkResult] = []
    skipped: list[str] = []

    wanted = set(scenarios)
    valid = {"parse", "lookup"}
    unknown = sorted(wanted - valid)
    if unknown:
        raise ValueError("unknown scenarios requested: " + ", ".join(unknown))

    if "parse" in wanted:
        results.extend(
            run_parse_scenarios(
                quick=quick,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

    if "lookup" in wanted:
        if issubclass(impl, AccessorPath):
            results.extend(
                run_lookup_scenarios(
                    impl,
                    quick=quick,
                    repeats=repeats,
                    warmup_loops=warmup_loops,
                )
            )
        else:
            skipped.append("lookup")

    meta = default_meta()
    meta["impl"] = f"{impl.__module__}.{impl.__qualname__}"
    meta["quick"] = quick
    meta["repeats"] = repeats
    meta["warmup_loops"] = warmup_loops
    meta["requested_scenarios"] = sorted(wanted)
    if skipped:
        meta["skipped_scenarios"] = skipped

    return results_to_json(results=results, meta=meta)
