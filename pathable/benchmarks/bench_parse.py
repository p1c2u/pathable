"""Standalone parse benchmark command."""

import argparse
from typing import Iterable

from pathable.benchmarks.core import add_common_args
from pathable.benchmarks.core import results_to_json
from pathable.benchmarks.core import write_json
from pathable.benchmarks.scenarios.parse import run_parse_scenarios


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    args = parser.parse_args(list(argv) if argv is not None else None)

    results = run_parse_scenarios(
        quick=args.quick,
        repeats=args.repeats,
        warmup_loops=args.warmup_loops,
    )

    payload = results_to_json(results=results)
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
