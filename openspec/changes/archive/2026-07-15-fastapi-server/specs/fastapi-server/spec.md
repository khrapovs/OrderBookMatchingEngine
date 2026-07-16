# fastapi-server

REST API specification for order book matching engine.

## ADDED Requirements

### Requirement: Place Orders

The system SHALL accept one or more orders via HTTP POST and add them to the order book without triggering matching.

#### Scenario: Place single limit order successfully
- **WHEN** client sends POST /orders with valid limit order
- **THEN** system returns 200 with confirmation and order details

#### Scenario: Place batch of orders successfully
- **WHEN** client sends POST /orders with multiple valid orders
- **THEN** system returns 200 with confirmation for all orders

#### Scenario: Place market order successfully
- **WHEN** client sends POST /orders with valid market order (no price)
- **THEN** system returns 200 with confirmation and order details

#### Scenario: Reject order with duplicate ID
- **WHEN** client sends order with ID that already exists in order book
- **THEN** system returns 400 with error message indicating duplicate ID

#### Scenario: Reject order with invalid data
- **WHEN** client sends order with missing required fields or invalid values
- **THEN** system returns 422 with validation errors

#### Scenario: Reject order with negative size
- **WHEN** client sends order with size ≤ 0
- **THEN** system returns 422 with validation error

### Requirement: Trigger Matching

The system SHALL execute order matching at a specified timestamp when explicitly requested.

#### Scenario: Match with no orders in book
- **WHEN** client sends POST /match with no orders in book
- **THEN** system returns 200 with empty trades list

#### Scenario: Match with non-crossing orders
- **WHEN** client sends POST /match with orders that don't cross (bid < offer)
- **THEN** system returns 200 with empty trades list and orders remain in book

#### Scenario: Match with crossing orders
- **WHEN** client sends POST /match with orders that cross (bid ≥ offer)
- **THEN** system returns 200 with executed trades and remaining orders updated

#### Scenario: Match with timestamp provided
- **WHEN** client sends POST /match with specific timestamp
- **THEN** system uses that timestamp for all executed trades

#### Scenario: Match with expired orders
- **WHEN** client sends POST /match with timestamp after some orders' expiration
- **THEN** system cancels expired orders and returns empty trades

### Requirement: Get Order Book State

The system SHALL return the current state of the order book including all unmatched orders.

#### Scenario: Get empty order book
- **WHEN** client sends GET /orders with no orders in book
- **THEN** system returns 200 with empty bids and offers

#### Scenario: Get order book with orders
- **WHEN** client sends GET /orders with orders in book
- **THEN** system returns 200 with bids and offers grouped by price

#### Scenario: Order book shows partial fills
- **WHEN** order is partially filled after matching
- **THEN** GET /orders shows remaining size for that order

### Requirement: Get Trade History

The system SHALL return all executed trades with optional timestamp filtering.

#### Scenario: Get empty trade history
- **WHEN** client sends GET /trades with no executed trades
- **THEN** system returns 200 with empty trades list

#### Scenario: Get all trades
- **WHEN** client sends GET /trades after some matches
- **THEN** system returns 200 with all executed trades

#### Scenario: Filter trades by timestamp
- **WHEN** client sends GET /trades?from_timestamp=<time>
- **THEN** system returns only trades at or after that timestamp

#### Scenario: Trades include all details
- **WHEN** trades are returned
- **THEN** each trade includes side, price, size, order IDs, trade ID, timestamp, execution type

### Requirement: Cancel Order

The system SHALL remove a specific order from the order book by ID.

#### Scenario: Cancel existing order
- **WHEN** client sends DELETE /orders/{id} for existing order
- **THEN** system returns 200 and removes order from book

#### Scenario: Cancel non-existent order
- **WHEN** client sends DELETE /orders/{id} for non-existent order
- **THEN** system returns 404 with error message

#### Scenario: Cancel already filled order
- **WHEN** client sends DELETE /orders/{id} for completely filled order
- **THEN** system returns 404 (order no longer in book)

### Requirement: Reset Engine State

The system SHALL clear all orders and trades and reinitialize the matching engine.

#### Scenario: Reset without seed
- **WHEN** client sends POST /reset with no seed
- **THEN** system clears all state and reinitializes with random seed

#### Scenario: Reset with seed
- **WHEN** client sends POST /reset with specific seed
- **THEN** system clears all state and reinitializes with that seed

#### Scenario: Reset clears order book
- **WHEN** client sends POST /reset after placing orders
- **THEN** GET /orders returns empty book

#### Scenario: Reset clears trade history
- **WHEN** client sends POST /reset after executing trades
- **THEN** GET /trades returns empty list

### Requirement: Get Order Book Summary

The system SHALL return aggregated order book levels with total size and count per price.

#### Scenario: Get empty summary
- **WHEN** client sends GET /summary with no orders
- **THEN** system returns 200 with empty summary

#### Scenario: Get summary with orders
- **WHEN** client sends GET /summary with orders at multiple prices
- **THEN** system returns aggregated bids and offers with total size and count per level

#### Scenario: Summary matches OrderBook.summary() format
- **WHEN** summary is returned
- **THEN** structure matches existing OrderBook.summary() polars schema

### Requirement: Client-Controlled Identifiers

The system SHALL accept client-provided order IDs and trader IDs without modification.

#### Scenario: Order ID preserved
- **WHEN** client provides order_id in request
- **THEN** system uses exact ID in order book and trades

#### Scenario: Trader ID preserved
- **WHEN** client provides trader_id in request
- **THEN** system uses exact ID in order and trade records

#### Scenario: No ID generation
- **WHEN** client omits order_id
- **THEN** system returns 422 validation error (ID required)

### Requirement: Client-Controlled Timestamps

The system SHALL accept client-provided timestamps for orders and matching without server time validation.

#### Scenario: Order timestamp preserved
- **WHEN** client provides timestamp in order request
- **THEN** system uses exact timestamp for order

#### Scenario: Match timestamp preserved
- **WHEN** client provides timestamp in match request
- **THEN** system uses exact timestamp for all executed trades

#### Scenario: No server time enforcement
- **WHEN** client provides past or future timestamps
- **THEN** system accepts them without validation

#### Scenario: Timestamp required for orders
- **WHEN** client omits timestamp in order request
- **THEN** system returns 422 validation error

### Requirement: Pydantic Validation

The system SHALL validate all request inputs using Pydantic models before processing.

#### Scenario: Invalid enum value
- **WHEN** client sends order with invalid side value (not "BUY" or "SELL")
- **THEN** system returns 422 with validation error

#### Scenario: Invalid order type
- **WHEN** client sends order with order_type other than "limit" or "market"
- **THEN** system returns 422 with validation error

#### Scenario: Market order with price
- **WHEN** client sends market order with price field
- **THEN** system returns 422 validation error (market orders have no price)

#### Scenario: Limit order without price
- **WHEN** client sends limit order without price field
- **THEN** system returns 422 with validation error

#### Scenario: Invalid timestamp format
- **WHEN** client sends invalid ISO datetime string
- **THEN** system returns 422 with validation error

### Requirement: Response Models

The system SHALL return all data using Pydantic response models with consistent structure.

#### Scenario: Order response includes all fields
- **WHEN** order is returned in response
- **THEN** response includes side, price, size, timestamp, order_id, trader_id, execution, status, expiration

#### Scenario: Trade response includes all fields
- **WHEN** trade is returned in response
- **THEN** response includes side, price, size, incoming_order_id, book_order_id, execution, trade_id, timestamp

#### Scenario: Enums serialized as strings
- **WHEN** response includes enum fields (side, execution, status)
- **THEN** values are string representations ("BUY", "SELL", "LIMIT", "MARKET", "OPEN")

#### Scenario: Timestamps serialized as ISO strings
- **WHEN** response includes timestamp fields
- **THEN** values are ISO 8601 formatted strings

### Requirement: Error Handling

The system SHALL return appropriate HTTP status codes and error messages for all failure cases.

#### Scenario: Validation error format
- **WHEN** request fails Pydantic validation
- **THEN** response is 422 with detailed field-level errors

#### Scenario: Business logic error format
- **WHEN** request fails business logic (duplicate ID, not found)
- **THEN** response includes clear error message and appropriate status code

#### Scenario: Internal error handling
- **WHEN** unexpected error occurs
- **THEN** system returns 500 without exposing internal details

### Requirement: State Isolation

The system SHALL maintain order book state across requests using a single global MatchingEngine instance.

#### Scenario: Orders persist across requests
- **WHEN** client places orders in one request
- **THEN** subsequent GET /orders shows those orders

#### Scenario: Trades accumulate across matches
- **WHEN** client triggers multiple matches
- **THEN** GET /trades shows all trades from all matches

#### Scenario: Partial fills persist
- **WHEN** order is partially filled in one match
- **THEN** remaining size is available for next match

#### Scenario: State cleared on reset
- **WHEN** client sends POST /reset
- **THEN** all orders and trades are cleared from state
