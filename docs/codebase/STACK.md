# Technology Stack

## Core Sections (Required)

### 1) Runtime Summary

| Area | Value | Evidence |
|------|-------|----------|
| Primary language | Python | pyproject.toml |
| Runtime + version | Python >=3.10, supports 3.10-3.14 | pyproject.toml line 19 |
| Package manager | uv | pyproject.toml lines 59-60 (build-system), README.md line 91 |
| Module/build system | uv_build (uv's build backend) | pyproject.toml line 60 |

### 2) Production Frameworks and Dependencies

List only high-impact production dependencies (frameworks, data, transport, auth).

| Dependency | Version | Role in system | Evidence |
|------------|---------|----------------|----------|
| numpy | >=2.2.6 | Numerical computations for order matching logic | pyproject.toml line 22 |
| faker | >=33.0.0 | Generating UUIDs for orders and trades | pyproject.toml line 21 |
| polars | >=1.42.1 (optional) | Optional data export to LazyFrame format | pyproject.toml line 28 |
| pandera[polars] | >=0.21.0 (optional) | Schema validation for polars dataframes | pyproject.toml line 27 |

### 3) Development Toolchain

| Tool | Purpose | Evidence |
|------|---------|----------|
| pytest | Test runner with coverage, benchmark, xdist | pyproject.toml lines 36-39 |
| pytest-cov | Code coverage measurement | pyproject.toml line 38 |
| pytest-benchmark[histogram] | Performance benchmarking | pyproject.toml line 37 |
| pytest-xdist | Parallel test execution | pyproject.toml line 39 |
| prek | Pre-commit hook management (wrapper) | pyproject.toml line 42 |
| ruff | Linter and formatter (Python) | pyproject.toml lines 66-83 |
| ty | Type checking | pyproject.toml line 43, lines 88-89 |
| mkdocs-material | Documentation site generation | pyproject.toml line 46 |
| mkdocstrings[python] | API doc generation from docstrings | pyproject.toml line 47 |

### 4) Key Commands

```bash
# Install dependencies (all groups and extras)
uv sync --all-groups --all-extras

# Build package
uv build

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=order_matching

# Run pre-commit checks (lint, format, type-check)
uv run prek run -v --show-diff-on-failure --all-files

# Install pre-commit hooks
uv run prek install

# Run benchmark
./benchmark.sh

# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build -s -c

# Publish to PyPI (production only)
uv publish
```

### 5) Environment and Config

- Config sources: pyproject.toml (project, tool configs), .pre-commit-config.yaml, mkdocs.yaml, .coveragerc
- Required env vars: None identified (library package, no runtime services)
- Deployment/runtime constraints: Pure Python library with optional polars support; Published to PyPI; Requires Python 3.10+

### 6) Evidence

- pyproject.toml
- .pre-commit-config.yaml
- .github/workflows/workflow.yaml
- README.md
- uv.lock
