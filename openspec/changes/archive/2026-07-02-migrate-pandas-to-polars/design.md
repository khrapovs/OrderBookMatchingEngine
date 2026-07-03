## Context

The OrderBookMatchingEngine currently uses pandas for DataFrame operations in three key areas:
1. `Orders.to_frame()` - converting order collections to DataFrames
2. `ExecutedTrades.to_frame()` - converting trade collections to DataFrames
3. `OrderBook.summary()` - generating order book summary DataFrames

All DataFrames are validated using pandera schemas (`OrderDataSchema`, `TradeDataSchema`, `OrderBookSummarySchema`) that define column types, constraints, and validation rules. These schemas are critical for downstream code and analysis pipelines.

**Current Implementation:**
- Uses `pandas.DataFrame.from_records()` to convert dataclass instances
- Uses pandas-specific operations like `.assign()` with lambda functions
- Type hints use `pandera.typing.pandas.DataFrame[Schema]`
- Schema validation uses pandera's pandas backend

**Constraints:**
- Must maintain 100% backward compatibility with existing DataFrame schemas
- Cannot break existing tests or downstream code that consumes these DataFrames

## Goals / Non-Goals

**Goals:**
- Replace pandas with polars for all DataFrame conversion operations
- Maintain identical DataFrame schemas (column names, types, constraints)
- Preserve all pandera validation behavior
- Improve performance through polars' optimized operations
- Update type hints to reflect polars usage while keeping schema validation
- Use LazyFrame and lazy evaluation whenever possible

**Non-Goals:**
- Changing the pandera schema definitions or validation rules
- Modifying the API surface (method signatures stay the same)
- Migrating internal data structures from dataclasses
- Supporting both pandas and polars simultaneously (full migration only)
- Changing behavior of existing methods beyond the DataFrame type

## Decisions

### Decision 1: Use polars DataFrame construction directly
**Rationale:** Polars provides native DataFrame construction from dictionaries and records. Instead of using pandas `from_records()`, we'll use `pl.LazyFrame()` constructor.

**Implementation:**
```python
# Before (pandas):
pd.DataFrame.from_records([asdict(order) for order in orders])

# After (polars):
pl.LazyFrame([asdict(order) for order in orders])
```

**Alternatives considered:**
- Converting pandas to polars via arrow - rejected as unnecessary intermediate step

### Decision 2: Handle type conversions with polars expressions
**Rationale:** Pandas uses `.assign()` with lambda functions for type conversions. Polars uses `.with_columns()` and expressions.

**Implementation:**
```python
# Before (pandas):
.assign(
    side=lambda df: df['side'].astype(str),
    timestamp=lambda df: pd.to_datetime(df['timestamp'])
)

# After (polars):
.with_columns([
    pl.col('side').cast(pl.Utf8),
    pl.col('timestamp').cast(pl.Datetime)
])
```

**Alternatives considered:**
- Keep using assign-style API via polars extensions - rejected for being less idiomatic

### Decision 3: Update pandera imports to support polars
**Rationale:** Pandera 0.17.0+ supports both pandas and polars backends through separate import paths.

**Implementation:**
```python
# Before:
from pandera.pandas import DataFrameModel
from pandera.typing.pandas import DataFrame

# After:
from pandera.polars import DataFrameModel
from pandera.typing.polars import DataFrame
from pandera.typing.polars import LazyFrame
```

**Alternatives considered:**
- Maintaining dual compatibility - rejected per non-goals (full migration only)
- Creating polars-specific schema copies - rejected to avoid duplication

### Decision 4: Handle empty DataFrames with explicit schema
**Rationale:** Empty polars DataFrames need explicit schema definition to maintain type information.

**Implementation:**
```python
# Empty DataFrame case:
if len(collection) == 0:
    return pl.DataFrame(schema={
        'column1': pl.Float64,
        'column2': pl.Utf8,
        # ... all columns
    })
```

**Alternatives considered:**
- Returning empty DataFrame without schema - rejected because pandera validation would fail
- Using schema inference from empty records - rejected as unreliable

## Risks / Trade-offs

**Risk:** Pandera polars support may have edge cases or bugs
- **Mitigation:** Comprehensive test suite covers all schema validation scenarios. Run full test suite before merging.

**Risk:** Polars API differences may cause subtle behavioral changes
- **Mitigation:** Carefully review all DataFrame operations and validate output schemas match exactly. Add explicit type casts where needed.

**Risk:** Breaking change for downstream code expecting pandas DataFrames
- **Mitigation:** This is intentional per requirements. Document clearly in CHANGELOG and update README examples.

**Trade-off:** Lose pandas ecosystem compatibility
- **Impact:** Code using these DataFrames must work with polars instead of pandas
- **Benefit:** Significantly better performance, especially for large order books

**Trade-off:** Increased dependency on polars library maturity
- **Impact:** Polars is newer than pandas, potential for API changes
- **Benefit:** Polars is stable (1.0+ released), actively developed, and widely adopted

## Migration Plan

**Phase 1: Update schemas**
1. Change imports in `src/order_matching/schemas.py` from pandas to polars
2. Update type hints to use `pandera.typing.polars.DataFrame`
3. Verify schemas still define the same constraints

**Phase 2: Update conversion methods**
1. Update `Orders.to_frame()` in `orders.py`
2. Update `ExecutedTrades.to_frame()` in `executed_trades.py`
3. Update `OrderBook.summary()` in `order_book.py`
4. Ensure each method handles empty cases with explicit schemas

**Phase 3: Update tests**
1. Run existing test suite - most should still pass
2. Fix any tests that check for pandas-specific behavior
3. Add new tests if needed for polars-specific edge cases

**Phase 4: Validate**
1. Run full test suite: `uv run pytest`
2. Run linter and formatter: `uv run prek run -v --show-diff-on-failure --all-files`

**Rollback strategy:**
- If tests fail after updates, revert changes file by file
- Git branch allows clean rollback to pandas implementation
- No database or persistent state changes, so rollback is safe

## Open Questions

None - requirements and approach are clear.
