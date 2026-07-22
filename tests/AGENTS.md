# Purpose

Comprehensive test suite covering core matching engine, API endpoints, simulation framework, and data exporters.

# Ownership

Owns all unit tests, integration tests, and benchmarks validating production code behavior.

# Local Contracts

**Structure mirrors source:**
- Root-level tests for core modules (test_matching_engine.py, test_order_book.py, etc.)
- `test_api/` - API endpoint and workflow tests
- `test_simulation/` - Market simulation and trader tests
- `test_exporters/` - Data export validation tests
- `conftest.py` - Shared pytest fixtures

**Test Rules:**
- Unit tests may NOT access private attributes/methods of classes
- Use public interfaces only
- Tests run with pytest and pytest-xdist for parallel execution
- Benchmarks use pytest-benchmark
- Doctests enabled for README.md and source docstrings

# Work Guidance

- Write tests first when fixing bugs (TDD encouraged)
- API tests use httpx TestClient
- Simulation tests verify trader behavior and market state transitions
- Coverage tracked via pytest-cov (config in .coveragerc)
- Run subset with `uv run pytest tests/test_api/` or similar

# Verification

```shell
uv run pytest
```

Run with coverage:
```shell
uv run pytest --cov=order_matching --cov-report=html
```

# Child DOX Index

None - test structure is self-documenting by mirroring source layout.
