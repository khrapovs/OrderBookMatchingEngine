# Testing Patterns

## Core Sections

### 1) Test Stack and Commands

- Primary test framework: **pytest** (version >=8.3.3)
- Assertion/mocking tools:
  - pytest built-in assertions
  - pytest fixtures (conftest.py)
  - numpy and faker for test data generation
  - pytest-benchmark for performance testing
- Commands:

```bash
# Run all tests (unit + doctests) with parallel execution
uv run pytest

# Run with coverage report
uv run pytest --cov=order_matching

# Run tests with coverage (CI mode)
uv run pytest --cov=order_matching --cov-config=.coveragerc

# Run benchmarks (normally disabled in default pytest run)
uv run pytest --benchmark-enable

# Run benchmark script (dedicated)
./benchmark.sh

# Run tests for specific module
uv run pytest tests/test_matching_engine.py

# Run tests in parallel (via xdist, enabled by default with -n=auto)
uv run pytest -n=auto
```

### 2) Test Layout

- Test file placement pattern: Separate `tests/` directory at project root, parallel to `src/` (pyproject.toml line 64)
- Naming convention: `test_*.py` (e.g., `test_matching_engine.py`, `test_order_book.py`, `test_orders.py`). 12 test files total.
- Setup files and where they run:
  - `tests/conftest.py`: Pytest fixtures for test data (e.g., `random_orders` fixture generates 1000 random orders for benchmarking)
  - `.coveragerc`: Coverage configuration
  - `tests/.benchmarks/`: Benchmark history storage

### 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|-------|----------|----------------|-------|
| Unit | Yes | Individual classes/methods (Order, OrderBook, MatchingEngine, Orders, ExecutedTrades) | 12 dedicated test files (test_order.py, test_order_book.py, test_matching_engine.py, etc.) |
| Integration | Partial | MatchingEngine with OrderBook interactions, exporter integration with schemas | Covered in test_matching_engine.py (full match flow) and test_exporter*.py |
| E2E | Yes (via doctests) | Complete user workflows from README examples | README.md and module docstrings include executable doctests (pyproject.toml line 63) |

### 4) Mocking and Isolation Strategy

- Main mocking approach: **Fixture-based test data** (no external services to mock)
- Isolation guarantees: Each test creates fresh instances of MatchingEngine, OrderBook, Orders, etc. No shared state between tests.
- Common failure mode in tests: Randomness without seed can cause flakiness (mitigated by using faker and numpy random generators with fixed seeds in fixtures—see conftest.py lines 13-15)

### 5) Coverage and Quality Signals

- Coverage tool + threshold: **pytest-cov** (pyproject.toml line 38), `.coveragerc` for config. No explicit threshold enforced in config.
- Current reported coverage: [TODO—run `uv run pytest --cov=order_matching --cov-report=term` to get current value]
- Known gaps/flaky areas:
  - No explicit edge case tests for order expiration race conditions
  - Benchmark tests in tests/.benchmarks/ may have timing variance

### 6) Evidence

- pyproject.toml lines 62-64 (pytest config: `--cov-config=.coveragerc --doctest-modules --doctest-glob='*.md' -n=auto --benchmark-disable`)
- tests/conftest.py (fixtures: `random_orders` fixture with faker and numpy)
- tests/ directory (12 test files: test_executed_trades.py, test_execution.py, test_exporter_base.py, test_exporters/, test_matching_engine.py, test_order.py, test_order_book.py, test_orders.py, test_random.py, test_side.py, test_status.py, test_trade.py)
- .github/workflows/workflow.yaml lines 11-34 (CI test execution across Python 3.10-3.14)
- .github/workflows/workflow.yaml lines 36-69 (benchmark job)
- README.md (doctests in usage examples)

## Extended Notes

- **Parallel execution**: Tests run with `pytest-xdist` (`-n=auto` flag) to parallelize across CPU cores (pyproject.toml line 63, line 39)
- **Benchmark isolation**: Benchmarks disabled by default (`--benchmark-disable` flag) to keep regular test runs fast. Run explicitly with `--benchmark-enable` or `./benchmark.sh` (pyproject.toml line 63)
- **Matrix testing in CI**: Tests run against Python 3.10, 3.11, 3.12, 3.13, 3.14 on ubuntu-latest in GitHub Actions (.github/workflows/workflow.yaml lines 16-18)
