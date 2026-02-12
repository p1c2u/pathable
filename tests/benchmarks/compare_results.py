"""Compare two pathable benchmark JSON results.

Exits non-zero if candidate regresses beyond the configured tolerance.

This is meant for local regression checking and optional CI gating.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Mapping
from typing import Tuple
from typing import cast


@dataclass(frozen=True)
class ScenarioComparison:
    name: str
    baseline_ops: float
    candidate_ops: float
    ratio: float


def _load(path: str) -> Mapping[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data_any = json.load(f)
    if not isinstance(data_any, dict):
        raise ValueError("Invalid report: expected top-level JSON object")
    return cast(Dict[str, Any], data_any)


def _extract_ops(report: Mapping[str, Any]) -> Dict[str, float]:
    benchmarks = report.get("benchmarks")
    if not isinstance(benchmarks, dict):
        raise ValueError("Invalid report: missing 'benchmarks' dict")

    benchmarks_d = cast(Dict[str, Any], benchmarks)

    out: Dict[str, float] = {}
    for name, payload in benchmarks_d.items():
        if not isinstance(payload, dict):
            continue
        payload_d = cast(Dict[str, Any], payload)
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
) -> Tuple[list[ScenarioComparison], list[ScenarioComparison]]:
    if tolerance < 0:
        raise ValueError("tolerance must be >= 0")

    b = _extract_ops(baseline)
    c = _extract_ops(candidate)

    comparisons: list[ScenarioComparison] = []
    for name in sorted(set(b) & set(c)):
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

    # Regression if candidate is slower by more than tolerance:
    # candidate_ops < baseline_ops * (1 - tolerance)
    floor_ratio = 1.0 - tolerance
    regressions = [x for x in comparisons if x.ratio < floor_ratio]
    return comparisons, regressions


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

    comparisons, regressions = compare(
        baseline=baseline,
        candidate=candidate,
        tolerance=args.tolerance,
    )

    print("scenario\tbaseline_ops/s\tcandidate_ops/s\tratio")
    for c in comparisons:
        print(
            f"{c.name}\t{c.baseline_ops:.2f}\t{c.candidate_ops:.2f}\t{c.ratio:.3f}"
        )

    if regressions:
        print("\nREGRESSIONS:")
        for r in regressions:
            print(
                f"- {r.name}: {r.ratio:.3f}x (baseline {r.baseline_ops:.2f} ops/s, candidate {r.candidate_ops:.2f} ops/s)"
            )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
