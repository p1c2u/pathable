"""Benchmarks for parsing and BasePath construction."""

import argparse
from typing import Iterable

from pathable.parsers import parse_args
from pathable.paths import BasePath

try:
    # Prefer module execution: `python -m tests.benchmarks.bench_parse ...`
    from .bench_utils import BenchmarkResult
    from .bench_utils import add_common_args
    from .bench_utils import results_to_json
    from .bench_utils import run_benchmark
    from .bench_utils import write_json
except ImportError:  # pragma: no cover
    # Allow direct execution: `python tests/benchmarks/bench_parse.py ...`
    from bench_utils import BenchmarkResult  # type: ignore[no-redef]
    from bench_utils import add_common_args  # type: ignore[no-redef]
    from bench_utils import results_to_json  # type: ignore[no-redef]
    from bench_utils import run_benchmark  # type: ignore[no-redef]
    from bench_utils import write_json  # type: ignore[no-redef]


def _build_args(n: int) -> list[object]:
    # Mix in segments that exercise splitting, filtering, bytes decode, and ints.
    out: list[object] = []
    for i in range(n):
        if i % 11 == 0:
            out.append(".")
        elif i % 11 == 1:
            out.append(b"bytes")
        elif i % 11 == 2:
            out.append(i)
        elif i % 11 == 3:
            out.append(f"a/{i}/b")
        else:
            out.append(f"seg{i}")
    return out


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    add_common_args(parser)
    args = parser.parse_args(list(argv) if argv is not None else None)

    repeats: int = args.repeats
    warmup_loops: int = args.warmup_loops

    results: list[BenchmarkResult] = []

    sizes = [10, 100, 1_000] if not args.quick else [10, 100]

    for n in sizes:
        inputs = _build_args(n)
        inputs_t = tuple(inputs)

        loops_parse = 80_000 if n <= 100 else 10_000
        if args.quick:
            loops_parse = min(loops_parse, 10_000)

        def do_parse(_inputs: tuple[object, ...] = inputs_t) -> None:
            parse_args(_inputs)

        results.append(
            run_benchmark(
                f"parse.parse_args.size{n}",
                do_parse,
                loops=loops_parse,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

        loops_basepath = 60_000 if n <= 100 else 3_000
        if args.quick:
            loops_basepath = min(loops_basepath, 5_000)

        def do_basepath(_inputs: tuple[object, ...] = inputs_t) -> None:
            BasePath(*_inputs)

        results.append(
            run_benchmark(
                f"paths.BasePath.constructor.size{n}",
                do_basepath,
                loops=loops_basepath,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

    payload = results_to_json(results=results)
    write_json(args.output, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
