## 1. Update Schema Definitions

- [ ] 2.1 Update imports in src/order_matching/schemas.py from `pandera.pandas` to `pandera.polars`
- [ ] 2.2 Update DataFrame type import from `pandera.typing.pandas` to `pandera.typing.polars`
- [ ] 2.3 Ensure all Field constraints (gt, ge, isin, unique, nullable) are preserved
- [ ] 2.4 Verify Config classes with strict=True remain unchanged
- [ ] 2.5 Run mypy to check type annotations are correct

## 2. Update Orders.to_frame() Method

- [ ] 3.1 Replace pandas import with polars in src/order_matching/orders.py
- [ ] 3.2 Update empty DataFrame case to return polars DataFrame with explicit OrderDataSchema schema
- [ ] 3.3 Replace `pd.DataFrame.from_records()` with `polars.DataFrame()` constructor
- [ ] 3.4 Replace `.assign()` with `.with_columns()` for type conversions (side, execution, status to string)
- [ ] 3.5 Update timestamp and expiration columns to use polars datetime casting
- [ ] 3.6 Update return type hint to `DataFrame[OrderDataSchema]` using polars typing
- [ ] 3.7 Verify method signature remains unchanged (backward compatible API)

## 3. Update ExecutedTrades.to_frame() Method

- [ ] 4.1 Replace pandas import with polars in src/order_matching/executed_trades.py
- [ ] 4.2 Update empty DataFrame case to return polars DataFrame with explicit TradeDataSchema schema
- [ ] 4.3 Replace `pd.DataFrame.from_records()` with `polars.DataFrame()` constructor
- [ ] 4.4 Replace `.assign()` with `.with_columns()` for type conversions (side, execution to string)
- [ ] 4.5 Update timestamp column to use polars datetime casting
- [ ] 4.6 Update return type hint to `DataFrame[TradeDataSchema]` using polars typing
- [ ] 4.7 Verify method signature remains unchanged

## 4. Update OrderBook.summary() Method

- [ ] 5.1 Replace pandas import with polars in src/order_matching/order_book.py
- [ ] 5.2 Replace pandas DataFrame construction in summary() with polars DataFrame
- [ ] 5.3 Update count column casting to use polars integer type
- [ ] 5.4 Replace `pd.concat()` with polars concatenation (use `pl.concat()`)
- [ ] 5.5 Update return type hint to `DataFrame[OrderBookSummarySchema]` using polars typing
- [ ] 5.6 Verify empty OrderBook case returns empty polars DataFrame
- [ ] 5.7 Update `get_imbalance()` method to work with polars DataFrames

## 5. Run Tests and Validate

- [ ] 6.1 Run full test suite: `uv run pytest`
- [ ] 6.2 Fix any tests in tests/test_order.py that check pandas-specific behavior
- [ ] 6.3 Fix any tests in tests/test_trade.py that check pandas-specific behavior
- [ ] 6.4 Fix any tests in tests/test_executed_trades.py that check pandas-specific behavior
- [ ] 6.5 Verify all pandera schema validations still pass
- [ ] 6.6 Check test coverage remains at current level

## 6. Type Checking and Linting

- [ ] 7.1 Run type checker: `uv run prek run -v --show-diff-on-failure --all-files`
- [ ] 7.2 Fix any type errors related to polars DataFrame usage

## 8. Documentation and Examples

- [ ] 8.1 Update README.md code examples to reflect polars DataFrames
- [ ] 8.2 Update any docstrings that mention pandas to reference polars
- [ ] 8.3 Verify documentation builds successfully: `uv run mkdocs build`
