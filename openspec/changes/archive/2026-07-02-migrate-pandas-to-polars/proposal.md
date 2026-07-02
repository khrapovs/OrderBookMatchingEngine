## Why

The project currently uses pandas for DataFrame operations in orders, trades, and order book summaries.
Polars offers significantly better performance and a more modern API, but the migration must maintain 100% schema compatibility with existing pandera validations to avoid breaking downstream code or analysis pipelines.

## What Changes

- Replace pandas DataFrame operations with polars equivalents across all data conversion methods
- Maintain pandera schema validation compatibility - all schemas must be converted to work polars DataFrames
- Update `to_frame()` methods in `Orders`, `ExecutedTrades`, and `OrderBook` classes to return polars DataFrames
- Ensure column names, dtypes, and constraints remain identical to current pandera-validated schemas
- Update type hints from `pandera.typing.pandas.DataFrame` to support polars while preserving schema validation

## Capabilities

### New Capabilities
- `polars-dataframe-conversion`: Converting internal data structures (Orders, ExecutedTrades, OrderBook) to polars DataFrames with schema validation
- `pandera-polars-validation`: Schema validation using pandera with polars backend to ensure schema compatibility

### Modified Capabilities

## Impact

**Code:**
- `src/order_matching/orders.py`: Update `to_frame()` method to use polars
- `src/order_matching/executed_trades.py`: Update `to_frame()` method to use polars
- `src/order_matching/order_book.py`: Update `summary()` method to use polars
- `src/order_matching/schemas.py`: Update schema definitions to support polars DataFrames

**Tests:**
- All existing tests that validate DataFrame schemas must continue to pass
- Tests in `tests/test_order.py`, `tests/test_trade.py`, `tests/test_executed_trades.py` that check DataFrame output
- Documentation examples in README.md that demonstrate DataFrame usage

**API:**
- Return type changes from pandas DataFrame to polars DataFrame, but schema validation ensures column names and dtypes remain compatible
