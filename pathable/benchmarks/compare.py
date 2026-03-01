"""Compare benchmark JSON results."""

import argparse
import json
from dataclasses import dataclass
from typing import Any
from typing import Iterable
from typing import Mapping
from typing import cast


@dataclass(frozen=True)
class ScenarioComparison:
    name: str
    baseline_ops: float
    candidate_ops: float
    ratio: float


@dataclass(frozen=True)
class CompareResult:
    comparisons: list[ScenarioComparison]
    regressions: list[ScenarioComparison]
    baseline_only: list[str]
    candidate_only: list[str]


def _load(path: str) -> Mapping[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data_any = json.load(f)
    if not isinstance(data_any, dict):
        raise ValueError("Invalid report: expected top-level JSON object")
    return cast(dict[str, Any], data_any)


def _extract_ops(report: Mapping[str, Any]) -> dict[str, float]:
    benchmarks = report.get("benchmarks")
    if not isinstance(benchmarks, dict):
        raise ValueError("Invalid report: missing 'benchmarks' dict")

    benchmarks_d = cast(dict[str, Any], benchmarks)

    out: dict[str, float] = {}
    for name, payload in benchmarks_d.items():
        if not isinstance(payload, dict):
            continue
        payload_d = cast(dict[str, Any], payload)
        ops_any = payload_d.get("median_ops_per_sec")
        ops = ops_any if isinstance(ops_any, (int, float)) else None
        if ops is not None:
            out[name] = float(ops)
    return out


def compare(
    *,
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    tolerance: float,
) -> CompareResult:
    if tolerance < 0:
        raise ValueError("tolerance must be >= 0")

    b = _extract_ops(baseline)
    c = _extract_ops(candidate)

    b_names = set(b)
    c_names = set(c)
    common_names = sorted(b_names & c_names)

    comparisons: list[ScenarioComparison] = []
    for name in common_names:
        bops = b[name]
        cops = c[name]
        ratio = cops / bops if bops > 0 else float("inf")
        comparisons.append(
            ScenarioComparison(
                name=name,
                baseline_ops=bops,
                candidate_ops=cops,
                ratio=ratio,
            )
        )

    floor_ratio = 1.0 - tolerance
    regressions = [x for x in comparisons if x.ratio < floor_ratio]

    return CompareResult(
        comparisons=comparisons,
        regressions=regressions,
        baseline_only=sorted(b_names - c_names),
        candidate_only=sorted(c_names - b_names),
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.20,
        help="Allowed slowdown (e.g. 0.20 means 20% slower allowed).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    baseline = _load(args.baseline)
    candidate = _load(args.candidate)

    result = compare(
        baseline=baseline,
        candidate=candidate,
        tolerance=args.tolerance,
    )

    common_count = len(result.comparisons)
    print(
        "scenarios: "
        f"common={common_count} "
        f"baseline_only={len(result.baseline_only)} "
        f"candidate_only={len(result.candidate_only)}"
    )

    if common_count == 0:
        print("ERROR: no overlapping scenarios between reports")
        return 1

    print("scenario\tbaseline_ops/s\tcandidate_ops/s\tratio")
    for row in result.comparisons:
        print(
            f"{row.name}\t{row.baseline_ops:.2f}\t{row.candidate_ops:.2f}\t{row.ratio:.3f}"
        )

    if result.regressions:
        print("\nREGRESSIONS:")
        for row in result.regressions:
            print(
                f"- {row.name}: {row.ratio:.3f}x "
                f"(baseline {row.baseline_ops:.2f} ops/s, "
                f"candidate {row.candidate_ops:.2f} ops/s)"
            )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
