# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

List only meaningful top-level directories and files.

| Path | Purpose | Evidence |
|------|---------|----------|
| src/order_matching/ | Core library source code (matching engine, order book, orders, trades) | Directory listing, pyproject.toml line 68 |
| tests/ | Test suite (12 test files) | Directory listing, pyproject.toml line 64 |
| docs/ | Documentation source files | Directory listing |
| docs_src/ | Documentation source templates | Directory listing |
| .github/workflows/ | CI/CD pipelines (tests, benchmarks, publishing) | .github/workflows/workflow.yaml |
| pyproject.toml | Project metadata, dependencies, tool configurations | File |
| README.md | Project overview, installation, basic usage | File |
| CHANGELOG.md | Version history and changes | File |
| mkdocs.yaml | MkDocs documentation configuration | File |
| .pre-commit-config.yaml | Pre-commit hook definitions (ruff, ty, builtin hooks) | File |
| benchmark.sh | Benchmark execution script | File |
| uv.lock | Dependency lock file managed by uv | File |

### 2) Entry Points

- Main runtime entry: `src/order_matching/matching_engine.py` (MatchingEngine class is the primary API)
- Secondary entry points (worker/cli/jobs): None (library package, not a service)
- How entry is selected (script/config): Users import `MatchingEngine` from `order_matching.matching_engine` module

### 3) Module Boundaries

| Boundary | What belongs here | What must not be here |
|----------|-------------------|------------------------|
| src/order_matching/ | Core matching logic, order/trade models, order book data structures, schema definitions, optional exporters | Tests, documentation, build artifacts |
| src/order_matching/exporters/ | Optional data export implementations (base, polars) | Core matching logic, order book state management |
| tests/ | Unit tests, integration tests, fixtures, benchmarks | Production code, documentation |
| docs_src/ | Documentation markdown source files | Source code, tests |

### 4) Naming and Organization Rules

- File naming pattern: `snake_case.py` (Python convention). Examples: `matching_engine.py`, `order_book.py`, `executed_trades.py`
- Directory organization pattern: Flat feature-based structure in `src/order_matching/` with one subdirectory (`exporters/`) for optional export functionality
- Import aliasing or path conventions: Absolute imports from `order_matching.*`; No path aliases detected; Standard Python import conventions

### 5) Evidence

- src/order_matching/ directory listing
- pyproject.toml lines 64, 68 (testpaths, src)
- File names: matching_engine.py, order_book.py, order.py, orders.py, executed_trades.py, trade.py, side.py, status.py, execution.py, schemas.py, random.py
