## 1. Update Schema Definitions

- [x] 1.1 Update imports in src/order_matching/schemas.py from `pandera.pandas` to `pandera.polars`
- [x] 1.2 Update DataFrame type import from `pandera.typing.pandas` to `pandera.typing.polars`
- [x] 1.3 Ensure all Field constraints (gt, ge, isin, unique, nullable) are preserved
- [x] 1.4 Verify Config classes with strict=True remain unchanged
- [x] 1.5 Run mypy to check type annotations are correct

## 2. Update Orders.to_frame() Method

- [x] 2.1 Replace pandas import with polars in src/order_matching/orders.py
- [x] 2.2 Update empty DataFrame case to return polars DataFrame with explicit OrderDataSchema schema
- [x] 2.3 Replace `pd.DataFrame.from_records()` with `polars.DataFrame()` constructor
- [x] 2.4 Replace `.assign()` with `.with_columns()` for type conversions (side, execution, status to string)
- [x] 2.5 Update timestamp and expiration columns to use polars datetime casting
- [x] 2.6 Update return type hint to `DataFrame[OrderDataSchema]` using polars typing
- [x] 2.7 Verify method signature remains unchanged (backward compatible API)

## 3. Update ExecutedTrades.to_frame() Method

- [x] 3.1 Replace pandas import with polars in src/order_matching/executed_trades.py
- [x] 3.2 Update empty DataFrame case to return polars DataFrame with explicit TradeDataSchema schema
- [x] 3.3 Replace `pd.DataFrame.from_records()` with `polars.DataFrame()` constructor
- [x] 3.4 Replace `.assign()` with `.with_columns()` for type conversions (side, execution to string)
- [x] 3.5 Update timestamp column to use polars datetime casting
- [x] 3.6 Update return type hint to `DataFrame[TradeDataSchema]` using polars typing
- [x] 3.7 Verify method signature remains unchanged

## 4. Update OrderBook.summary() Method

- [x] 4.1 Replace pandas import with polars in src/order_matching/order_book.py
- [x] 4.2 Replace pandas DataFrame construction in summary() with polars DataFrame
- [x] 4.3 Update count column casting to use polars integer type
- [x] 4.4 Replace `pd.concat()` with polars concatenation (use `pl.concat()`)
- [x] 4.5 Update return type hint to `DataFrame[OrderBookSummarySchema]` using polars typing
- [x] 4.6 Verify empty OrderBook case returns empty polars DataFrame
- [x] 4.7 Update `get_imbalance()` method to work with polars DataFrames

## 5. Run Tests and Validate

- [x] 5.1 Run full test suite: `uv run pytest`
- [x] 5.2 Fix any tests in tests/test_order.py that check pandas-specific behavior
- [x] 5.3 Fix any tests in tests/test_trade.py that check pandas-specific behavior
- [x] 5.4 Fix any tests in tests/test_executed_trades.py that check pandas-specific behavior
- [x] 5.5 Verify all pandera schema validations still pass
- [x] 5.6 Check test coverage remains at current level

## 6. Type Checking and Linting

- [x] 6.1 Run type checker: `uv run prek run -v --show-diff-on-failure --all-files`
- [x] 6.2 Fix any type errors related to polars DataFrame usage

## 7. Documentation and Examples

- [x] 7.1 Update README.md code examples to reflect polars DataFrames
- [x] 7.2 Update any docstrings that mention pandas to reference polars
- [x] 7.3 Verify documentation builds successfully: `uv run mkdocs build`
