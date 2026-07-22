# Purpose

Provides data export functionality converting order books, trades, and engine state to external data formats (currently Polars LazyFrames).

# Ownership

Owns export interfaces and implementations for different data backends.

# Local Contracts

- `base.py` - Abstract base exporter interface
- `polars.py` - Polars LazyFrame exporter implementation
- Optional dependency: users install with `pip install order-matching[polars]`
- Core engine has no dependency on exporters

**Export Targets:**
- Orders collections → Polars LazyFrame with order schema
- ExecutedTrades → Polars LazyFrame with trade schema
- Pandera schemas validate output structure

# Work Guidance

- Keep exporters loosely coupled from core engine
- Each exporter implements `BaseExporter` protocol
- Export methods accept core domain objects (Orders, ExecutedTrades)
- Schema validation via Pandera when Polars is installed
- Avoid pulling in heavy dependencies at module import time

# Verification

```shell
uv run pytest tests/test_exporters/
```

# Child DOX Index

None - small focused module with clear structure.
