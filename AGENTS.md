# Agent Notes for pathable

This file is a concise, repo-specific guide for agentic coding tools.
If anything here conflicts with code or CI, follow the code/CI.

## Quick facts
- Primary language: Python (>=3.9)
- Build/packaging: Poetry
- Tests: pytest + coverage
- Lint/format: black, isort, flynt (pre-commit)
- Types: mypy (strict)

## Build, lint, and test commands

### Setup
- Create virtualenv and install deps: `poetry install`
- Optional dev hooks: `poetry install --with dev`
- Pre-commit hooks: `poetry run pre-commit install`

### Tests
- Run full suite: `poetry run pytest`
- Run a single test file: `poetry run pytest tests/unit/test_paths.py`
- Run a single test function: `poetry run pytest tests/unit/test_paths.py::TestBasePathInit::test_default`
- Run tests by keyword: `poetry run pytest -k "BasePath"`
- Coverage reports are written to:
  - `reports/junit.xml`
  - `reports/coverage.xml`

### Type checking
- Run mypy: `poetry run mypy`

### Formatting / linting
- Black format: `poetry run black pathable tests`
- isort (single-line imports): `poetry run isort --filter-files pathable tests`
- flynt (f-string conversion): `poetry run flynt pathable tests`
- All hooks (recommended): `poetry run pre-commit run --all-files`

## Code style guidelines

### Imports
- Prefer absolute imports from `pathable.*`.
- Group imports: standard library, third-party, then local.
- Use one import per line (isort is configured with `force_single_line = true`).
- Keep ordering stable; let isort manage it.

### Formatting
- Black is authoritative; line length is 79.
- Favor black-compatible formatting in new code.
- Keep docstrings short and focused; use triple double quotes.

### Types
- Mypy runs in strict mode; add type hints for public APIs.
- Use `typing` generics and `TypeVar` where appropriate (see `pathable/accessors.py`).
- Return precise types instead of `Any` unless the API requires it.
- Prefer `Optional[T]` or `Union[T, None]` over implicit `None`.

### Naming
- Classes: `PascalCase`.
- Functions/vars: `snake_case`.
- Constants: `UPPER_CASE`.
- Type variables: short, uppercase (`T`, `K`, `V`, etc.).

### Error handling
- Use precise exceptions (`TypeError`, `ValueError`, `KeyError`, `AttributeError`).
- Avoid broad `except Exception` unless re-raising with context.
- Ensure exceptions are deterministic and message text is stable.

### Data model and patterns
- Paths are immutable; methods return new instances (see `BasePath`).
- Preserve cached properties and avoid side effects in `@cached_property`.
- Use `@dataclass(frozen=True, init=False)` where immutability is intended.
- Keep public API methods small and composable.

### Strings and bytes
- Treat bytes as ASCII when decoding path parts (see `parse_args`).
- Prefer f-strings for formatting; flynt can help.

### Testing
- Tests use pytest; keep tests explicit and readable.
- Favor direct assertions, not helper wrappers.
- Use deterministic inputs; avoid reliance on filesystem unless necessary.

## Repository conventions
- Code lives under `pathable/`.
- Tests live under `tests/`.
- CI runs: `pytest` and `mypy` (see `.github/workflows/python-test.yml`).
- Formatting is enforced by pre-commit hooks in `.pre-commit-config.yaml`.

## Rules files
- No Cursor rules found in `.cursor/rules/` or `.cursorrules`.
- No Copilot rules found in `.github/copilot-instructions.md`.

## Notes for agents
- Prefer editing minimal sections; do not reformat unrelated code.
- Run targeted tests when possible (single file or single test).
- Keep changes compatible with Python 3.9+.
