## ADDED Requirements

### Requirement: Convert Orders to polars DataFrame
The system SHALL convert `Orders` objects to polars DataFrames using the `to_frame()` method with all columns matching the `OrderDataSchema`.

#### Scenario: Convert empty Orders to DataFrame
- **WHEN** `to_frame()` is called on an empty `Orders` object
- **THEN** system returns an empty polars DataFrame

#### Scenario: Convert populated Orders to DataFrame
- **WHEN** `to_frame()` is called on `Orders` containing one or more orders
- **THEN** system returns a polars DataFrame with columns: timestamp, expiration, order_id, trader_id, side, execution, status, price, size, price_number_of_digits
- **THEN** all string enum fields (side, execution, status) are converted to string representations
- **THEN** timestamp and expiration columns are datetime type

### Requirement: Convert ExecutedTrades to polars DataFrame
The system SHALL convert `ExecutedTrades` objects to polars DataFrames using the `to_frame()` method with all columns matching the `TradeDataSchema`.

#### Scenario: Convert empty ExecutedTrades to DataFrame
- **WHEN** `to_frame()` is called on an empty `ExecutedTrades` object
- **THEN** system returns an empty polars DataFrame

#### Scenario: Convert populated ExecutedTrades to DataFrame
- **WHEN** `to_frame()` is called on `ExecutedTrades` containing one or more trades
- **THEN** system returns a polars DataFrame with columns: timestamp, incoming_order_id, book_order_id, trade_id, side, execution, price, size
- **THEN** string enum fields (side, execution) are converted to string representations
- **THEN** timestamp column is datetime type

### Requirement: Convert OrderBook to polars DataFrame summary
The system SHALL convert `OrderBook` objects to polars DataFrames using the `summary()` method with all columns matching the `OrderBookSummarySchema`.

#### Scenario: Convert empty OrderBook to summary DataFrame
- **WHEN** `summary()` is called on an empty `OrderBook`
- **THEN** system returns an empty polars DataFrame

#### Scenario: Convert OrderBook with bids and offers to summary
- **WHEN** `summary()` is called on `OrderBook` containing bids and/or offers
- **THEN** system returns a polars DataFrame with columns: side, price, size, count
- **THEN** each unique price level is represented as a single row
- **THEN** count column is integer type
- **THEN** side column contains "BUY" or "SELL" string values

### Requirement: Maintain DataFrame schema compatibility
The system SHALL ensure polars DataFrames produced by conversion methods have identical column names, dtypes, and value formats as the pandas DataFrames they replace.

#### Scenario: Column names match exactly
- **WHEN** any conversion method produces a polars DataFrame
- **THEN** column names MUST match the corresponding pandera schema field names exactly

#### Scenario: Data types are compatible
- **WHEN** any conversion method produces a polars DataFrame
- **THEN** numeric columns (price, size, count) use appropriate numeric types
- **THEN** datetime columns use polars datetime type
- **THEN** string columns (order_id, trader_id, trade_id, side, execution, status) use string type

#### Scenario: Empty DataFrames have correct schema
- **WHEN** conversion methods are called on empty collections
- **THEN** resulting empty DataFrames MUST still have the correct column names and types defined
