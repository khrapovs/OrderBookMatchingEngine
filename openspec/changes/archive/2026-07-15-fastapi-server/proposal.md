## Why

The order book matching engine is currently a Python library designed for programmatic use. For demo, education, and backtesting scenarios, users need a RESTful API to interact with the matching engine through HTTP requests rather than Python code. This enables web-based demos, language-agnostic integrations, and step-by-step exploration of order book mechanics without requiring Python knowledge.

## What Changes

- Add FastAPI server wrapping the existing `MatchingEngine` with REST endpoints
- Create Pydantic models for API request/response validation (separate from existing dataclasses)
- Implement endpoints for order placement, matching execution, and state inspection
- Add state management with global `MatchingEngine` instance and reset capability
- Create comprehensive test suite using FastAPI's `TestClient`
- Maintain full compatibility with existing library - no changes to core matching logic

## Capabilities

### New Capabilities
- `fastapi-server`: REST API server for order book matching engine with endpoints for order placement, matching execution, order book inspection, trade history, and state management

### Modified Capabilities
<!-- No existing capabilities are being modified - this is purely additive -->

## Impact

**Code:**
- New `src/order_matching/api/` package with FastAPI application and routers
- New `src/order_matching/api/models/` for Pydantic schemas
- New `tests/test_api/` for API endpoint tests

**Dependencies:**
- Add `fastapi` as required dependency
- Add `pydantic` as required dependency
- Add `uvicorn` as required dependency for running server

**APIs:**
- New REST API with 7 endpoints (non-breaking, additive only)
- Existing library API unchanged

**Systems:**
- Optional HTTP server component (can still use library directly)
