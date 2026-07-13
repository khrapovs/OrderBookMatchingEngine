# Codebase Concerns

## Core Sections (Required)

### 1) Top Risks (Prioritized)

| Severity | Concern | Evidence | Impact | Suggested action |
|----------|---------|----------|--------|------------------|
| Medium | Polars imported unconditionally in order_book.py despite being optional dependency | order_book.py lines 5-6 import polars/pandera without TYPE_CHECKING guard | Breaks for users who install without `[polars]` extra when using OrderBook.summary() or get_imbalance() | Move polars imports inside TYPE_CHECKING block or make methods conditional on polars availability |
| Medium | No thread safety in MatchingEngine | matching_engine.py modifies shared state (order book, queue) without locks | Concurrent match() calls would corrupt order book state, produce incorrect trades | Document thread-safety limitations or add locking mechanism |
| Low | State mutation during iteration over price levels | matching_engine.py lines 102-118 modifies OrderBook while iterating | Potential for iteration bugs if logic changes; current implementation is careful but fragile | Consider collecting modifications first, then applying after iteration |
| Low | Deprecated method still present | executed_trades.py lines 60-74: to_frame() deprecated in 0.5.0, planned removal in 1.0.0 | Users may still use deprecated API; maintenance burden | Add runtime warning and update all examples/docs to use PolarsExporter |

### 2) Technical Debt

List the most important debt items only.

| Debt item | Why it exists | Where | Risk if ignored | Suggested fix |
|-----------|---------------|-------|-----------------|---------------|
| No persistence layer | Library design—state management delegated to users | MatchingEngine, OrderBook | Users must implement save/restore if needed; no guidance provided | Add persistence examples to docs or create optional persistence module |
| OrderBook summary() returns polars LazyFrame unconditionally | Early design decision before polars became optional | order_book.py lines 52-98 | Breaks optional dependency model | Refactor to return dict/list, add optional polars converter method |
| No custom exception types | Assertions used for internal validation | matching_engine.py line 76, line 121 | Unclear error messages for library users; assertion failures not documented | Define OrderMatchingError hierarchy, replace assertions with typed exceptions |

### 3) Security Concerns

| Risk | OWASP category (if applicable) | Evidence | Current mitigation | Gap |
|------|--------------------------------|----------|--------------------|-----|
| Denial of service via large order books | N/A (no web interface) | OrderBook stores unlimited orders in memory dicts | None | Document memory limits, add optional order count/size limits |
| Unvalidated numeric inputs | A03:2021 Injection (indirect) | Order price/size validated only by type hints, no range checks | price_number_of_digits rounds prices (order.py line 25) | Add explicit validation for price > 0, size > 0, reasonable ranges |

**Note**: As a library with no network I/O, most OWASP Top 10 risks do not apply. Main risks are resource exhaustion and numeric validation.

### 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---------|----------|-----------------|-------------|-----------------------|
| O(n) price level iteration | matching_engine.py lines 96-100 iterate all matching prices | None currently | High order count at same price level would slow matching | Use priority queue or skip empty price levels |
| OrderBook stores all orders in memory | order_book.py dicts hold all open orders | None currently (library use case) | Long-running engines with many orders would exhaust memory | Add order expiration cleanup, document memory usage expectations |
| No batch matching optimization | matching_engine.py processes one order at a time | None currently | High-frequency trading scenarios would be slow | Add batch matching mode for multiple orders at same timestamp |

### 5) Fragile/High-Churn Areas

| Area | Why fragile | Churn signal | Safe change strategy |
|------|-------------|-------------|----------------------|
| pyproject.toml | Frequent dependency updates, version bumps | 13 changes in last 90 days (highest churn file) | Test all dependency combinations in CI matrix |
| order_book.py | Complex state management with multiple indexes (bids, offers, orders_by_expiration) | 3 changes in last 90 days | Comprehensive unit tests for add/remove/match scenarios; validate index consistency |
| orders.py | Core data structure for queue and collections | 3 changes in last 90 days | Test queue operations (add, remove, dequeue) with edge cases (empty, single, many) |

### 6) `[ASK USER]` Questions

None—all architectural and functional questions resolved by inspection.

### 7) Evidence

- Codebase scan output (docs/codebase/.codebase-scan.txt)
  - High-churn files section (lines 407-428): pyproject.toml (13), uv.lock (9), order_book.py (3), orders.py (3)
  - No TODO/FIXME/HACK found in production code (line 382-383)
- order_book.py lines 5-6 (unconditional polars import)
- order_book.py lines 52-98 (summary() returns LazyFrame)
- executed_trades.py lines 60-74 (deprecated to_frame() method)
- matching_engine.py lines 102-118 (state mutation during iteration)
- matching_engine.py line 76, line 121 (assertions for internal state)
- order.py line 25 (price rounding only validation)
- pyproject.toml lines 26-32 (polars as optional dependency)

## Extended Notes

### Recent Improvements

Based on git history (lines 386-405 in scan output):
- Version 0.5.0 (latest): Separated data export to optional module (commit 84d0b43)
- Version 0.4.0: Migrated from pandas to polars (commit 73297f3)
- Recent fixes: Non-removal of filled orders from orders_by_expiration (commit e5a2d69)
- Recent refactors: Removed mypy, now using ty for type checking (commit d62925e)

These show active maintenance and architectural improvements (pandas→polars migration, export separation).

### No Critical Bugs Found

- Zero TODO/FIXME/HACK markers in production code
- Recent bug fix for order expiration handling suggests issues are being addressed
- Comprehensive test coverage with doctests, unit tests, and benchmarks
