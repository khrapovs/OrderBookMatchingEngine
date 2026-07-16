# Implementation Tasks

## 1. Package Structure Setup

- [x] 1.1 Create `src/order_matching/api/` directory structure
- [x] 1.2 Create `src/order_matching/api/models/` directory for Pydantic schemas
- [x] 1.3 Create `tests/test_api/` directory for API tests
- [x] 1.4 Create `__init__.py` files for all new packages
- [x] 1.5 Add FastAPI CLI entrypoint to pyproject.toml: `[tool.fastapi]` section with `entrypoint = "order_matching.api.app:app"`

## 2. Pydantic Request Models

**NOTE:** Follow FastAPI best practices - do NOT use ellipsis (`...`) for required fields. Use `Field(gt=0)` for constraints.

- [x] 2.1 Create `src/order_matching/api/models/requests.py`
- [x] 2.2 Implement `OrderBase` with common fields (side, size, timestamp, order_id, trader_id, expiration) - required fields have no default, no ellipsis
- [x] 2.3 Implement `LimitOrderRequest` extending `OrderBase` with price field
- [x] 2.4 Implement `MarketOrderRequest` extending `OrderBase` without price field
- [x] 2.5 Create discriminated union `OrderRequest` using Pydantic's Field(discriminator="order_type")
- [x] 2.6 Implement `PlaceOrdersRequest` with list of `OrderRequest`
- [x] 2.7 Implement `MatchRequest` with timestamp field
- [x] 2.8 Implement `ResetRequest` with optional seed field
- [x] 2.9 Add validation constraints using Field(gt=0) WITHOUT ellipsis - required fields simply have no default value

## 3. Pydantic Response Models

- [x] 3.1 Create `src/order_matching/api/models/responses.py`
- [x] 3.2 Implement `OrderResponse` with all order fields
- [x] 3.3 Implement `TradeResponse` with all trade fields
- [x] 3.4 Implement `PlaceOrdersResponse` with confirmation message and orders list
- [x] 3.5 Implement `MatchResponse` with executed trades list
- [x] 3.6 Implement `OrderBookResponse` with bids and offers dictionaries
- [x] 3.7 Implement `TradeHistoryResponse` with trades list
- [x] 3.8 Implement `ResetResponse` with confirmation message
- [x] 3.9 Implement `ErrorResponse` for error messages

## 4. Domain Converters

- [x] 4.1 Create `src/order_matching/api/models/converters.py`
- [x] 4.2 Implement `request_to_domain_order()` converting Pydantic request to Order/LimitOrder/MarketOrder
- [x] 4.3 Implement `domain_order_to_response()` converting Order to OrderResponse
- [x] 4.4 Implement `domain_trade_to_response()` converting Trade to TradeResponse
- [x] 4.5 Implement `domain_orders_to_response()` converting Orders collection to list of OrderResponse
- [x] 4.6 Implement `domain_trades_to_response()` converting ExecutedTrades to list of TradeResponse
- [x] 4.7 Add enum conversion helpers (Side/Execution/Status to/from strings)
- [x] 4.8 Add error handling for invalid enum values

## 5. FastAPI Dependencies

**NOTE:** Use `Annotated` pattern for dependency injection per FastAPI best practices.

- [x] 5.1 Create `src/order_matching/api/dependencies.py`
- [x] 5.2 Implement `get_matching_engine()` dependency function returning global engine from app.state
- [x] 5.3 Create type alias: `MatchingEngineDep = Annotated[MatchingEngine, Depends(get_matching_engine)]` for reusability

## 6. FastAPI Routes - Place Orders

**NOTE:** Use `def` (not `async def`) for all endpoints - MatchingEngine operations are synchronous. Use return types (not response_model parameter).

- [x] 6.1 Create `src/order_matching/api/routes.py`
- [x] 6.2 Implement `POST /orders` endpoint accepting PlaceOrdersRequest with return type `-> PlaceOrdersResponse`
- [x] 6.3 Use `engine: MatchingEngineDep` parameter for dependency injection (Annotated pattern)
- [x] 6.4 Convert request orders to domain Orders using converters
- [x] 6.5 Call `matching_engine.match(orders=..., timestamp=...)` with orders and first order's timestamp
- [x] 6.6 Return PlaceOrdersResponse with success message
- [x] 6.7 Add error handling for duplicate order IDs (400 response)
- [x] 6.8 Add Pydantic validation error handling (422 response)

## 7. FastAPI Routes - Match Orders

- [x] 7.1 Implement `POST /match` endpoint accepting MatchRequest with return type `-> MatchResponse`
- [x] 7.2 Use `engine: MatchingEngineDep` parameter for dependency injection
- [x] 7.3 Call `matching_engine.match(orders=None, timestamp=request.timestamp)`
- [x] 7.4 Convert ExecutedTrades to TradeResponse list using converters
- [x] 7.5 Return MatchResponse with executed trades
- [x] 7.6 Handle empty trades case (return empty list)

## 8. FastAPI Routes - Get Order Book

- [x] 8.1 Implement `GET /orders` endpoint with return type `-> OrderBookResponse`
- [x] 8.2 Use `engine: MatchingEngineDep` parameter for dependency injection
- [x] 8.3 Access `matching_engine.unprocessed_orders.bids` and `offers`
- [x] 8.4 Convert OrderBook data structure to OrderBookResponse
- [x] 8.5 Return structured bids and offers with orders grouped by price
- [x] 8.6 Handle empty order book case

## 9. FastAPI Routes - Get Trades

- [x] 9.1 Implement `GET /trades` endpoint with optional `from_timestamp` query parameter and return type `-> TradeHistoryResponse`
- [x] 9.2 Use `engine: MatchingEngineDep` parameter for dependency injection
- [x] 9.3 Access all executed trades from engine state (accumulate across match calls)
- [x] 9.4 Filter trades by timestamp if parameter provided
- [x] 9.5 Convert trades to TradeResponse list using converters
- [x] 9.6 Return TradeHistoryResponse
- [x] 9.7 Handle empty trades case

## 10. FastAPI Routes - Cancel Order

- [x] 10.1 Implement `DELETE /orders/{order_id}` endpoint with path parameter using Annotated
- [x] 10.2 Use `engine: MatchingEngineDep` parameter for dependency injection
- [x] 10.3 Find order in `matching_engine.unprocessed_orders` by order_id
- [x] 10.4 Create Order with Status.CANCEL and call match() to remove it
- [x] 10.5 Return success response (200)
- [x] 10.6 Handle order not found case (404 response)

## 11. FastAPI Routes - Reset Engine

- [x] 11.1 Implement `POST /reset` endpoint accepting ResetRequest with return type `-> ResetResponse`
- [x] 11.2 Create new MatchingEngine instance with seed from request (or None)
- [x] 11.3 Replace `app.state.engine` with new instance
- [x] 11.4 Clear any accumulated trade history
- [x] 11.5 Return ResetResponse with confirmation message

## 12. FastAPI Routes - Get Summary

- [x] 12.1 Implement `GET /summary` endpoint with return type for summary response
- [x] 12.2 Use `engine: MatchingEngineDep` parameter for dependency injection
- [x] 12.3 Call `matching_engine.unprocessed_orders.summary()`
- [x] 12.4 Convert polars LazyFrame to JSON-serializable format
- [x] 12.5 Return summary response
- [x] 12.6 Handle empty order book case

## 13. FastAPI Application

- [x] 13.1 Create `src/order_matching/api/app.py`
- [x] 13.2 Create FastAPI app instance with title and description
- [x] 13.3 Initialize global MatchingEngine in app.state on startup
- [x] 13.4 Include router from routes.py
- [x] 13.5 Add CORS middleware (permissive for demo use)
- [x] 13.6 Add global exception handler for unexpected errors (500)
- [x] 13.7 Add validation exception handler for Pydantic errors (422)

## 14. Trade History Management

- [x] 14.1 Add trade accumulation mechanism (store ExecutedTrades from all match calls)
- [x] 14.2 Update `POST /match` to store returned trades in app.state
- [x] 14.3 Update `GET /trades` to return accumulated trades
- [x] 14.4 Update `POST /reset` to clear accumulated trades
- [x] 14.5 Ensure trades persist across multiple match operations

## 15. Duplicate Order ID Validation

- [x] 15.1 Implement order ID tracking in MatchingEngine state
- [x] 15.2 Add validation in `POST /orders` to check for duplicate IDs
- [x] 15.3 Return 400 error with clear message for duplicates
- [x] 15.4 Update reset to clear ID tracking

## 16. Test Setup

- [x] 16.1 Create `tests/test_api/conftest.py`
- [x] 16.2 Add `client` fixture using FastAPI TestClient
- [x] 16.3 Add `reset_engine` fixture to ensure clean state per test
- [x] 16.4 Add helper fixtures for common test data (sample orders, timestamps)

## 17. Test - Place Orders Endpoint

- [x] 17.1 Create `tests/test_api/test_place_orders.py`
- [x] 17.2 Test successful single limit order placement
- [x] 17.3 Test successful batch order placement
- [x] 17.4 Test successful market order placement
- [x] 17.5 Test duplicate order ID rejection (400)
- [x] 17.6 Test invalid data rejection (422)
- [x] 17.7 Test negative size rejection (422)
- [x] 17.8 Test missing required fields rejection (422)

## 18. Test - Match Endpoint

- [x] 18.1 Create `tests/test_api/test_match.py`
- [x] 18.2 Test match with empty order book
- [x] 18.3 Test match with non-crossing orders (no execution)
- [x] 18.4 Test match with crossing orders (execution occurs)
- [x] 18.5 Test match timestamp is used in trades
- [x] 18.6 Test match with expired orders (cancellation)
- [x] 18.7 Test partial fills

## 19. Test - Get Orders Endpoint

- [x] 19.1 Create `tests/test_api/test_get_orders.py`
- [x] 19.2 Test get empty order book
- [x] 19.3 Test get order book with buy orders only
- [x] 19.4 Test get order book with sell orders only
- [x] 19.5 Test get order book with mixed orders
- [x] 19.6 Test orders grouped by price correctly
- [x] 19.7 Test partial fills reflected in returned sizes

## 20. Test - Get Trades Endpoint

- [x] 20.1 Create `tests/test_api/test_get_trades.py`
- [x] 20.2 Test get empty trade history
- [x] 20.3 Test get trades after successful match
- [x] 20.4 Test trades accumulate across multiple matches
- [x] 20.5 Test filter trades by timestamp
- [x] 20.6 Test trade response includes all required fields

## 21. Test - Cancel Order Endpoint

- [x] 21.1 Create `tests/test_api/test_cancel_order.py`
- [x] 21.2 Test cancel existing order successfully
- [x] 21.3 Test cancel non-existent order (404)
- [x] 21.4 Test cancel already filled order (404)
- [x] 21.5 Test order removed from order book after cancel

## 22. Test - Reset Endpoint

- [x] 22.1 Create `tests/test_api/test_reset.py`
- [x] 22.2 Test reset without seed clears state
- [x] 22.3 Test reset with seed reinitializes engine
- [x] 22.4 Test reset clears order book
- [x] 22.5 Test reset clears trade history
- [x] 22.6 Test operations work correctly after reset

## 23. Test - Summary Endpoint

- [x] 23.1 Create `tests/test_api/test_summary.py`
- [x] 23.2 Test summary with empty order book
- [x] 23.3 Test summary with orders at multiple price levels
- [x] 23.4 Test summary aggregates size and count correctly
- [x] 23.5 Test summary format matches OrderBook.summary() schema

## 24. Test - End-to-End Workflows

- [x] 24.1 Create `tests/test_api/test_workflows.py`
- [x] 24.2 Test complete workflow: reset → place → view → match → view trades
- [x] 24.3 Test multiple match cycles with order accumulation
- [x] 24.4 Test backtesting scenario with historical timestamps
- [x] 24.5 Test educational demo scenario (step-by-step observation)

## 25. Documentation

- [x] 25.1 Add API usage examples to README.md
- [x] 25.2 Document endpoint specifications (request/response formats)
- [x] 25.3 Add example curl commands for each endpoint
- [x] 25.4 Document how to run the server with uvicorn
- [x] 25.5 Add API limitations (single-user, in-memory, demo use)
- [x] 25.6 Create example notebook or script demonstrating backtesting workflow

## 26. Dependencies and Build

- [x] 26.1 Add API server startup script or entry point in pyproject.toml
- [x] 26.2 Update pre-commit hooks if needed for new files

## 27. Final Verification

- [x] 27.1 Run all tests with `uv run pytest tests/test_api/`
- [x] 27.2 Run all existing tests to ensure no regressions
- [x] 27.3 Start server with `fastapi dev` and manually test each endpoint
- [x] 27.4 Test with curl/httpie for real HTTP behavior
- [x] 27.5 Verify error responses are user-friendly
- [x] 27.6 Verify all endpoints use return types (not response_model parameter)
- [x] 27.7 Verify all endpoints use `def` (not `async def`)
- [x] 27.8 Verify dependency injection uses Annotated pattern
- [x] 27.9 Run linter with `uv run prek run -v --show-diff-on-failure --all-files` and fix all prek failures
