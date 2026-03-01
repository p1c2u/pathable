"""Standalone lookup benchmark command."""

import argparse
from typing import Iterable
from typing import cast

from pathable.benchmarks.core import add_common_args
from pathable.benchmarks.core import default_meta
from pathable.benchmarks.core import results_to_json
from pathable.benchmarks.core import write_json
from pathable.benchmarks.registry import resolve_impl
from pathable.benchmarks.scenarios.lookup import run_lookup_scenarios
from pathable.paths import AccessorPath


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    parser.add_argument(
        "--impl",
        default="pathable.LookupPath",
        help="AccessorPath implementation target (default: pathable.LookupPath).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    impl = resolve_impl(args.impl)
    if not issubclass(impl, AccessorPath):
        raise TypeError(
            "lookup benchmark requires an AccessorPath implementation"
        )
    accessor_impl = cast(type[AccessorPath[object, object, object]], impl)

    results = run_lookup_scenarios(
        accessor_impl,
        quick=args.quick,
        repeats=args.repeats,
        warmup_loops=args.warmup_loops,
    )

    meta = default_meta()
    meta["impl"] = f"{impl.__module__}.{impl.__qualname__}"

    payload = results_to_json(results=results, meta=meta)
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
