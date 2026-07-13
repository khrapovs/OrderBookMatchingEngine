# Coding Conventions

## Core Sections

### 1) Naming Rules

| Item | Rule | Example | Evidence |
|------|------|---------|----------|
| Files | snake_case.py | matching_engine.py, order_book.py, executed_trades.py | src/order_matching/ directory |
| Functions/methods | snake_case, descriptive verb phrases | `match()`, `get_imbalance()`, `_execute_trades()` | matching_engine.py, order_book.py |
| Classes | PascalCase | `MatchingEngine`, `OrderBook`, `LimitOrder`, `ExecutedTrades` | All source files |
| Private methods | Leading underscore: `_method_name` | `_match()`, `_execute_trade()`, `_get_expired_orders()` | matching_engine.py lines 74-134 |
| Constants/enum values | UPPER_SNAKE_CASE for enum values | `Side.BUY`, `Side.SELL`, `Status.OPEN`, `Status.CANCEL` | side.py, status.py |
| Type aliases | PascalCase with `Type` suffix | `OrderBookOrdersType = dict[float, Orders]` | order_book.py line 13 |

### 2) Formatting and Linting

- Formatter: **ruff-format** (`.pre-commit-config.yaml` line 21-23)
- Linter: **ruff** (`.pre-commit-config.yaml` line 17-20, `pyproject.toml` lines 66-83)
- Most relevant enforced rules:
  - Line length: 120 characters (pyproject.toml line 67)
  - Select: E (pycodestyle errors), F (pyflakes), D (pydocstyle), B (bugbear), I (isort), ARG (unused arguments), ANN (type annotations) (pyproject.toml line 71)
  - Docstring convention: NumPy style (pyproject.toml line 86)
  - Ignore: D100-D107 (missing docstrings for modules/classes/methods, except public functions), D213, D417 (pyproject.toml lines 72-83)
- Run commands:
  ```bash
  # Run linter with auto-fix
  uv run ruff check --fix

  # Run formatter
  uv run ruff format

  # Run via pre-commit (includes ty type-check)
  uv run prek run -v --show-diff-on-failure --all-files
  ```

### 3) Import and Module Conventions

- Import grouping/order: Enforced by ruff isort (I rules). Standard library, third-party, local imports separated by blank lines (pyproject.toml line 71)
- Alias vs relative import policy: Absolute imports from `order_matching.*` used throughout. No relative imports detected. Examples: `from order_matching.order import Order`, `from order_matching.side import Side`
- Public exports/barrel policy: No `__all__` exports defined. Main module `__init__.py` only contains version detection (src/order_matching/__init__.py)

### 4) Error and Logging Conventions

- Error strategy by layer: Assertions used for internal state validation (e.g., `assert self._timestamp is not None` in matching_engine.py line 76, line 121). No custom exception types defined. Type validation handled by dataclasses and type hints.
- Logging style and required context fields: No logging library detected in codebase. Library pattern—users are responsible for logging in their applications.
- Sensitive-data redaction rules: Not applicable (no PII or secrets in order matching library)

### 5) Testing Conventions

- Test file naming/location rule: `test_*.py` files in `tests/` directory, separate from source. Examples: `test_matching_engine.py`, `test_order_book.py`, `test_orders.py` (tests/ directory listing)
- Mocking strategy norm: Use pytest fixtures for test data generation. Faker with fixed seeds for reproducible random data (tests/conftest.py). No external service mocking needed (library has no I/O).
- Coverage expectation: Coverage measured with pytest-cov, run in CI with `--cov=order_matching` flag (.github/workflows/workflow.yaml line 34). No explicit threshold set in config. Doctests enabled for README.md and module docstrings (pyproject.toml line 63).

### 6) Evidence

- pyproject.toml (lines 66-89: ruff config, lines 62-64: pytest config)
- .pre-commit-config.yaml (lines 15-29: ruff and ty hooks)
- src/order_matching/matching_engine.py (naming, assertions)
- src/order_matching/order_book.py (naming, type aliases)
- tests/conftest.py (fixture conventions)
- .github/workflows/workflow.yaml (test execution)
