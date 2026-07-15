# Implementation Tasks

## 1. Package Structure Setup

- [ ] 1.1 Create `src/order_matching/api/` directory structure
- [ ] 1.2 Create `src/order_matching/api/models/` directory for Pydantic schemas
- [ ] 1.3 Create `tests/test_api/` directory for API tests
- [ ] 1.4 Create `__init__.py` files for all new packages

## 2. Pydantic Request Models

- [ ] 2.1 Create `src/order_matching/api/models/requests.py`
- [ ] 2.2 Implement `OrderBase` with common fields (side, size, timestamp, order_id, trader_id, expiration)
- [ ] 2.3 Implement `LimitOrderRequest` extending `OrderBase` with price field
- [ ] 2.4 Implement `MarketOrderRequest` extending `OrderBase` without price field
- [ ] 2.5 Create discriminated union `OrderRequest` using Pydantic's Field(discriminator="order_type")
- [ ] 2.6 Implement `PlaceOrdersRequest` with list of `OrderRequest`
- [ ] 2.7 Implement `MatchRequest` with timestamp field
- [ ] 2.8 Implement `ResetRequest` with optional seed field
- [ ] 2.9 Add validation constraints (size > 0, price > 0 for limit orders)

## 3. Pydantic Response Models

- [ ] 3.1 Create `src/order_matching/api/models/responses.py`
- [ ] 3.2 Implement `OrderResponse` with all order fields
- [ ] 3.3 Implement `TradeResponse` with all trade fields
- [ ] 3.4 Implement `PlaceOrdersResponse` with confirmation message and orders list
- [ ] 3.5 Implement `MatchResponse` with executed trades list
- [ ] 3.6 Implement `OrderBookResponse` with bids and offers dictionaries
- [ ] 3.7 Implement `TradeHistoryResponse` with trades list
- [ ] 3.8 Implement `ResetResponse` with confirmation message
- [ ] 3.9 Implement `ErrorResponse` for error messages

## 4. Domain Converters

- [ ] 4.1 Create `src/order_matching/api/models/converters.py`
- [ ] 4.2 Implement `request_to_domain_order()` converting Pydantic request to Order/LimitOrder/MarketOrder
- [ ] 4.3 Implement `domain_order_to_response()` converting Order to OrderResponse
- [ ] 4.4 Implement `domain_trade_to_response()` converting Trade to TradeResponse
- [ ] 4.5 Implement `domain_orders_to_response()` converting Orders collection to list of OrderResponse
- [ ] 4.6 Implement `domain_trades_to_response()` converting ExecutedTrades to list of TradeResponse
- [ ] 4.7 Add enum conversion helpers (Side/Execution/Status to/from strings)
- [ ] 4.8 Add error handling for invalid enum values

## 5. FastAPI Dependencies

- [ ] 5.1 Create `src/order_matching/api/dependencies.py`
- [ ] 5.2 Implement `get_matching_engine()` dependency returning global engine from app.state
- [ ] 5.3 Add type hints for dependency injection

## 6. FastAPI Routes - Place Orders

- [ ] 6.1 Create `src/order_matching/api/routes.py`
- [ ] 6.2 Implement `POST /orders` endpoint accepting PlaceOrdersRequest
- [ ] 6.3 Convert request orders to domain Orders using converters
- [ ] 6.4 Call `matching_engine.match(orders=..., timestamp=...)` with orders and first order's timestamp
- [ ] 6.5 Return PlaceOrdersResponse with success message
- [ ] 6.6 Add error handling for duplicate order IDs (400 response)
- [ ] 6.7 Add Pydantic validation error handling (422 response)

## 7. FastAPI Routes - Match Orders

- [ ] 7.1 Implement `POST /match` endpoint accepting MatchRequest
- [ ] 7.2 Call `matching_engine.match(orders=None, timestamp=request.timestamp)`
- [ ] 7.3 Convert ExecutedTrades to TradeResponse list using converters
- [ ] 7.4 Return MatchResponse with executed trades
- [ ] 7.5 Handle empty trades case (return empty list)

## 8. FastAPI Routes - Get Order Book

- [ ] 8.1 Implement `GET /orders` endpoint
- [ ] 8.2 Access `matching_engine.unprocessed_orders.bids` and `offers`
- [ ] 8.3 Convert OrderBook data structure to OrderBookResponse
- [ ] 8.4 Return structured bids and offers with orders grouped by price
- [ ] 8.5 Handle empty order book case

## 9. FastAPI Routes - Get Trades

- [ ] 9.1 Implement `GET /trades` endpoint with optional `from_timestamp` query parameter
- [ ] 9.2 Access all executed trades from engine state (accumulate across match calls)
- [ ] 9.3 Filter trades by timestamp if parameter provided
- [ ] 9.4 Convert trades to TradeResponse list using converters
- [ ] 9.5 Return TradeHistoryResponse
- [ ] 9.6 Handle empty trades case

## 10. FastAPI Routes - Cancel Order

- [ ] 10.1 Implement `DELETE /orders/{order_id}` endpoint
- [ ] 10.2 Find order in `matching_engine.unprocessed_orders` by order_id
- [ ] 10.3 Create Order with Status.CANCEL and call match() to remove it
- [ ] 10.4 Return success response (200)
- [ ] 10.5 Handle order not found case (404 response)

## 11. FastAPI Routes - Reset Engine

- [ ] 11.1 Implement `POST /reset` endpoint accepting ResetRequest
- [ ] 11.2 Create new MatchingEngine instance with seed from request (or None)
- [ ] 11.3 Replace `app.state.engine` with new instance
- [ ] 11.4 Clear any accumulated trade history
- [ ] 11.5 Return ResetResponse with confirmation message

## 12. FastAPI Routes - Get Summary

- [ ] 12.1 Implement `GET /summary` endpoint
- [ ] 12.2 Call `matching_engine.unprocessed_orders.summary()`
- [ ] 12.3 Convert polars LazyFrame to JSON-serializable format
- [ ] 12.4 Return summary response
- [ ] 12.5 Handle empty order book case

## 13. FastAPI Application

- [ ] 13.1 Create `src/order_matching/api/app.py`
- [ ] 13.2 Create FastAPI app instance with title and description
- [ ] 13.3 Initialize global MatchingEngine in app.state on startup
- [ ] 13.4 Include router from routes.py
- [ ] 13.5 Add CORS middleware (permissive for demo use)
- [ ] 13.6 Add global exception handler for unexpected errors (500)
- [ ] 13.7 Add validation exception handler for Pydantic errors (422)

## 14. Trade History Management

- [ ] 14.1 Add trade accumulation mechanism (store ExecutedTrades from all match calls)
- [ ] 14.2 Update `POST /match` to store returned trades in app.state
- [ ] 14.3 Update `GET /trades` to return accumulated trades
- [ ] 14.4 Update `POST /reset` to clear accumulated trades
- [ ] 14.5 Ensure trades persist across multiple match operations

## 15. Duplicate Order ID Validation

- [ ] 15.1 Implement order ID tracking in MatchingEngine state
- [ ] 15.2 Add validation in `POST /orders` to check for duplicate IDs
- [ ] 15.3 Return 400 error with clear message for duplicates
- [ ] 15.4 Update reset to clear ID tracking

## 16. Test Setup

- [ ] 16.1 Create `tests/test_api/conftest.py`
- [ ] 16.2 Add `client` fixture using FastAPI TestClient
- [ ] 16.3 Add `reset_engine` fixture to ensure clean state per test
- [ ] 16.4 Add helper fixtures for common test data (sample orders, timestamps)

## 17. Test - Place Orders Endpoint

- [ ] 17.1 Create `tests/test_api/test_place_orders.py`
- [ ] 17.2 Test successful single limit order placement
- [ ] 17.3 Test successful batch order placement
- [ ] 17.4 Test successful market order placement
- [ ] 17.5 Test duplicate order ID rejection (400)
- [ ] 17.6 Test invalid data rejection (422)
- [ ] 17.7 Test negative size rejection (422)
- [ ] 17.8 Test missing required fields rejection (422)

## 18. Test - Match Endpoint

- [ ] 18.1 Create `tests/test_api/test_match.py`
- [ ] 18.2 Test match with empty order book
- [ ] 18.3 Test match with non-crossing orders (no execution)
- [ ] 18.4 Test match with crossing orders (execution occurs)
- [ ] 18.5 Test match timestamp is used in trades
- [ ] 18.6 Test match with expired orders (cancellation)
- [ ] 18.7 Test partial fills

## 19. Test - Get Orders Endpoint

- [ ] 19.1 Create `tests/test_api/test_get_orders.py`
- [ ] 19.2 Test get empty order book
- [ ] 19.3 Test get order book with buy orders only
- [ ] 19.4 Test get order book with sell orders only
- [ ] 19.5 Test get order book with mixed orders
- [ ] 19.6 Test orders grouped by price correctly
- [ ] 19.7 Test partial fills reflected in returned sizes

## 20. Test - Get Trades Endpoint

- [ ] 20.1 Create `tests/test_api/test_get_trades.py`
- [ ] 20.2 Test get empty trade history
- [ ] 20.3 Test get trades after successful match
- [ ] 20.4 Test trades accumulate across multiple matches
- [ ] 20.5 Test filter trades by timestamp
- [ ] 20.6 Test trade response includes all required fields

## 21. Test - Cancel Order Endpoint

- [ ] 21.1 Create `tests/test_api/test_cancel_order.py`
- [ ] 21.2 Test cancel existing order successfully
- [ ] 21.3 Test cancel non-existent order (404)
- [ ] 21.4 Test cancel already filled order (404)
- [ ] 21.5 Test order removed from order book after cancel

## 22. Test - Reset Endpoint

- [ ] 22.1 Create `tests/test_api/test_reset.py`
- [ ] 22.2 Test reset without seed clears state
- [ ] 22.3 Test reset with seed reinitializes engine
- [ ] 22.4 Test reset clears order book
- [ ] 22.5 Test reset clears trade history
- [ ] 22.6 Test operations work correctly after reset

## 23. Test - Summary Endpoint

- [ ] 23.1 Create `tests/test_api/test_summary.py`
- [ ] 23.2 Test summary with empty order book
- [ ] 23.3 Test summary with orders at multiple price levels
- [ ] 23.4 Test summary aggregates size and count correctly
- [ ] 23.5 Test summary format matches OrderBook.summary() schema

## 24. Test - End-to-End Workflows

- [ ] 24.1 Create `tests/test_api/test_workflows.py`
- [ ] 24.2 Test complete workflow: reset → place → view → match → view trades
- [ ] 24.3 Test multiple match cycles with order accumulation
- [ ] 24.4 Test backtesting scenario with historical timestamps
- [ ] 24.5 Test educational demo scenario (step-by-step observation)

## 25. Documentation

- [ ] 25.1 Add API usage examples to README.md
- [ ] 25.2 Document endpoint specifications (request/response formats)
- [ ] 25.3 Add example curl commands for each endpoint
- [ ] 25.4 Document how to run the server with uvicorn
- [ ] 25.5 Add API limitations (single-user, in-memory, demo use)
- [ ] 25.6 Create example notebook or script demonstrating backtesting workflow

## 26. Dependencies and Build

- [ ] 26.1 Add API server startup script or entry point in pyproject.toml
- [ ] 26.2 Update pre-commit hooks if needed for new files

## 27. Final Verification

- [ ] 27.1 Run all tests with `uv run pytest tests/test_api/`
- [ ] 27.2 Run all existing tests to ensure no regressions
- [ ] 27.3 Start server and manually test each endpoint
- [ ] 27.4 Test with curl/httpie for real HTTP behavior
- [ ] 27.5 Verify error responses are user-friendly
- [ ] 27.6 Run linter with `uv run prek run -v --show-diff-on-failure --all-files` and fix all prek failures
