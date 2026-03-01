"""Benchmarks for parsing and BasePath construction."""

from pathable.benchmarks.core import BenchmarkResult
from pathable.benchmarks.core import run_benchmark
from pathable.paths import BasePath


def _build_args(n: int) -> list[object]:
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


def run_parse_scenarios(
    *, quick: bool, repeats: int, warmup_loops: int
) -> list[BenchmarkResult]:
    results: list[BenchmarkResult] = []
    sizes = [10, 100, 1_000] if not quick else [10, 100]

    for n in sizes:
        inputs = _build_args(n)
        inputs_t = tuple(inputs)

        loops_parse = 80_000 if n <= 100 else 10_000
        if quick:
            loops_parse = min(loops_parse, 10_000)

        def do_parse(_inputs: tuple[object, ...] = inputs_t) -> None:
            BasePath._parse_args(_inputs)

        results.append(
            run_benchmark(
                f"parse.BasePath._parse_args.size{n}",
                do_parse,
                loops=loops_parse,
                repeats=repeats,
                warmup_loops=warmup_loops,
            )
        )

        loops_basepath = 60_000 if n <= 100 else 3_000
        if quick:
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

    return results
