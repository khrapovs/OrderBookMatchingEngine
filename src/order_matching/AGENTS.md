# Purpose

Core order matching engine package providing price-time priority matching, order management, trade execution, and optional API/simulation/export features.

# Ownership

Owns the matching engine core logic, data structures, and feature modules (api, simulation, exporters).

# Local Contracts

**Core Modules (root level):**
- `matching_engine.py` - Main engine orchestrating order placement and matching
- `order_book.py` - Order book data structure with bid/ask management
- `order.py`, `orders.py` - Order domain objects (limit/market orders) and collections
- `executed_trades.py`, `trade.py` - Trade results and individual trade records
- `enums.py` - Shared enums (Side, OrderType, Execution)
- `schemas.py` - Shared data schemas
- `random.py` - Randomness utilities with reproducible seeding

**Architecture:**
- Core modules have no dependencies on api/simulation/exporters
- api/simulation/exporters import from core but not each other
- All classes follow privacy convention: public interface minimal, internal details prefixed with `_`

# Work Guidance

- Keep core matching logic independent of API/simulation/export concerns
- Price-time priority matching is the central algorithm
- Orders placed via `place()` do not execute until `match()` is called
- All timestamp-based operations accept `datetime` objects
- Unit tests must not access private attributes/methods

# Verification

Run from repository root:
```shell
uv run pytest tests/test_matching_engine.py tests/test_order_book.py tests/test_order.py tests/test_orders.py tests/test_trade.py tests/test_executed_trades.py
```

# Child DOX Index

- `api/AGENTS.md` - FastAPI REST API for remote matching engine control
- `simulation/AGENTS.md` - Discrete-time market simulation with traders and news feed
- `exporters/AGENTS.md` - Data export to Polars LazyFrames
