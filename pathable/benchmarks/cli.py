"""CLI entrypoint for pathable benchmarks."""

import argparse
from typing import Iterable

from pathable.benchmarks.compare import main as compare_main
from pathable.benchmarks.core import write_json
from pathable.benchmarks.run import run_all


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathable-bench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run benchmark scenarios")
    run_parser.add_argument(
        "--impl",
        required=True,
        help="Implementation target, e.g. pathable.LookupPath",
    )
    run_parser.add_argument("--output", required=True)
    run_parser.add_argument("--quick", action="store_true")
    run_parser.add_argument("--repeats", type=int, default=5)
    run_parser.add_argument("--warmup-loops", type=int, default=1)
    run_parser.add_argument(
        "--scenario",
        action="append",
        choices=["parse", "lookup"],
        help=(
            "Run only selected scenario groups. Repeat flag to select multiple; "
            "defaults to both parse and lookup."
        ),
    )

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare benchmark JSON reports",
    )
    compare_parser.add_argument("--baseline", required=True)
    compare_parser.add_argument("--candidate", required=True)
    compare_parser.add_argument("--tolerance", type=float, default=0.20)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "run":
        scenarios = (
            tuple(args.scenario) if args.scenario else ("parse", "lookup")
        )
        payload = run_all(
            impl_target=args.impl,
            quick=args.quick,
            repeats=args.repeats,
            warmup_loops=args.warmup_loops,
            scenarios=scenarios,
        )
        write_json(args.output, payload)
        return 0

    if args.command == "compare":
        return compare_main(
            [
                "--baseline",
                args.baseline,
                "--candidate",
                args.candidate,
                "--tolerance",
                str(args.tolerance),
            ]
        )

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
