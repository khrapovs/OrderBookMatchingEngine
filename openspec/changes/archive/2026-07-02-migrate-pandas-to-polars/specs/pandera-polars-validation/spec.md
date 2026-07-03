## ADDED Requirements

### Requirement: Validate polars DataFrames with pandera schemas
The system SHALL use pandera to validate polars DataFrames against existing schema definitions (`OrderDataSchema`, `TradeDataSchema`, `OrderBookSummarySchema`).

#### Scenario: Valid polars DataFrame passes schema validation
- **WHEN** a polars DataFrame with correct schema is validated against `OrderDataSchema`, `TradeDataSchema`, or `OrderBookSummarySchema`
- **THEN** validation succeeds without errors

#### Scenario: Invalid polars DataFrame fails schema validation
- **WHEN** a polars DataFrame with incorrect schema (wrong columns, wrong types, or constraint violations) is validated
- **THEN** validation raises a pandera validation error with details

### Requirement: Maintain schema constraint validation
The system SHALL validate all pandera Field constraints (gt, ge, isin, unique, nullable) on polars DataFrames.

#### Scenario: Price constraint validation
- **WHEN** a polars DataFrame contains price values <= 0
- **THEN** validation against schemas with `price: Field(gt=0)` fails

#### Scenario: Enum value constraint validation
- **WHEN** a polars DataFrame contains invalid enum values in side/execution/status columns
- **THEN** validation against schemas with `Field(isin=[...])` fails

#### Scenario: Unique constraint validation
- **WHEN** a polars DataFrame for OrderBookSummary contains duplicate price values
- **THEN** validation against `OrderBookSummarySchema` with `price: Field(unique=True)` fails

#### Scenario: Nullable constraint validation
- **WHEN** a polars DataFrame contains null values in non-nullable columns
- **THEN** validation fails
- **WHEN** a polars DataFrame contains null values in nullable columns (e.g., expiration)
- **THEN** validation succeeds

### Requirement: Update schema type hints for polars
The system SHALL update type hints in schema definitions to support both pandas and polars DataFrames via pandera's typing system.

#### Scenario: Schema works with pandera.typing.polars.DataFrame and pandera.typing.polars.LazyFrame
- **WHEN** schemas are imported and used with polars DataFrames
- **THEN** type hints correctly indicate polars DataFrame compatibility

### Requirement: Preserve strict mode behavior
The system SHALL maintain strict mode validation configured in schema Config classes when validating polars DataFrames.

#### Scenario: Strict schema rejects extra columns
- **WHEN** a polars DataFrame with extra columns is validated against a schema with `strict = True`
- **THEN** validation fails

#### Scenario: Strict schema accepts exact columns
- **WHEN** a polars DataFrame with exact required columns is validated against a schema with `strict = True`
- **THEN** validation succeeds
