import json
from pathlib import Path

import pytest

from pathable.benchmarks.compare import compare
from pathable.benchmarks.compare import main as compare_main
from pathable.benchmarks.registry import resolve_impl
from pathable.benchmarks.run import run_all
from tests.benchmarks import bench_lookup
from tests.benchmarks import bench_parse
from tests.benchmarks import compare_results


def test_resolve_impl_by_dotted_name() -> None:
    impl = resolve_impl("pathable.LookupPath")
    assert impl.__name__ == "LookupPath"


def test_compare_uses_only_overlapping_scenarios() -> None:
    baseline = {
        "benchmarks": {
            "same": {"median_ops_per_sec": 100.0},
            "baseline_only": {"median_ops_per_sec": 100.0},
        }
    }
    candidate = {
        "benchmarks": {
            "same": {"median_ops_per_sec": 85.0},
            "candidate_only": {"median_ops_per_sec": 200.0},
        }
    }

    result = compare(
        baseline=baseline,
        candidate=candidate,
        tolerance=0.10,
    )

    assert [x.name for x in result.comparisons] == ["same"]
    assert [x.name for x in result.regressions] == ["same"]
    assert result.baseline_only == ["baseline_only"]
    assert result.candidate_only == ["candidate_only"]


def test_compare_main_fails_on_no_overlap(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    candidate_path = tmp_path / "candidate.json"

    baseline_path.write_text(
        json.dumps({"benchmarks": {"a": {"median_ops_per_sec": 1.0}}}),
        encoding="utf-8",
    )
    candidate_path.write_text(
        json.dumps({"benchmarks": {"b": {"median_ops_per_sec": 1.0}}}),
        encoding="utf-8",
    )

    code = compare_main(
        [
            "--baseline",
            str(baseline_path),
            "--candidate",
            str(candidate_path),
        ]
    )
    assert code == 1


def test_run_all_can_limit_to_lookup_scenarios() -> None:
    payload = run_all(
        impl_target="pathable.LookupPath",
        quick=True,
        repeats=1,
        warmup_loops=0,
        scenarios=("lookup",),
    )
    benchmarks = payload["benchmarks"]
    assert benchmarks
    assert all(name.startswith("lookup.") for name in benchmarks)


@pytest.mark.parametrize(
    "module",
    [bench_lookup, bench_parse, compare_results],
)
def test_compat_wrapper_emits_deprecation_warning(module: object) -> None:
    with pytest.warns(DeprecationWarning):
        # Delegate may fail due to missing required args; warning is what matters.
        try:
            getattr(module, "main")([])
        except SystemExit:
            pass
