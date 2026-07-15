## Context

The order book matching engine exists as a Python library with core domain models (`Order`, `Trade`, `MatchingEngine`) implemented as dataclasses. The library is stateful - `MatchingEngine` maintains an order book that accumulates across multiple `match()` calls. The primary use cases are demo, education, and backtesting scenarios where users need to control timing and observe state between operations.

**Current State:**
- Core library: `MatchingEngine`, `Order`/`LimitOrder`/`MarketOrder`, `Trade`, `Orders`, `ExecutedTrades`
- Dataclasses with domain logic, no HTTP/API layer
- Client-controlled: timestamps, order IDs, matching trigger points

**Constraints:**
- Must reuse existing domain models without modification
- Single market (no multi-market complexity)
- No persistence layer (in-memory only for demos)
- No authentication/authorization (educational tool)

## Goals / Non-Goals

**Goals:**
- Provide RESTful API for programmatic and web-based interaction
- Enable two-step workflow: place orders, then explicitly trigger matching
- Support backtesting with client-controlled timestamps
- Maintain full compatibility with existing library (no breaking changes)
- Clear separation between placing orders and executing matches
- Batch order placement for efficiency

**Non-Goals:**
- Production-grade features (authentication, rate limiting, persistence)
- Multi-market support (single global order book only)
- Real-time websocket feeds (REST only)
- Order modification (use cancel + new order)
- Historical state replay (no event sourcing)
- Horizontal scaling (single process, in-memory state)

## Decisions

### Decision 1: Global Singleton MatchingEngine

**Choice:** Single `MatchingEngine` instance stored in `app.state.engine`

**Rationale:**
- Matches library usage pattern (stateful accumulation)
- Single market use case doesn't require multiple instances
- Simplifies state management for demo/education scenarios
- Reset endpoint provides clean slate for new experiments

**Alternatives Considered:**
- Per-request instance: Would lose state between calls, defeating purpose
- Market-scoped instances: Over-engineering for single market requirement
- Session-based: Adds complexity without clear benefit for demos

**Trade-offs:**
- No concurrency safety (acceptable for educational tool)
- No horizontal scaling (out of scope)
- Requires explicit reset between scenarios (provides clear boundary)

### Decision 2: Pydantic Models Separate from Domain Models

**Choice:** Create parallel Pydantic models for API validation, convert to/from domain dataclasses

**Rationale:**
- Domain models are dataclasses (not Pydantic BaseModel)
- API needs different representations (enums as strings, discriminated unions)
- Separation allows API evolution without touching core library
- Conversion layer explicitly handles impedance mismatch

**Structure:**
```
API Layer (Pydantic)           Domain Layer (dataclasses)
─────────────────────          ──────────────────────────
OrderRequest                   Order
├─ LimitOrderRequest      →    ├─ LimitOrder
└─ MarketOrderRequest     →    └─ MarketOrder

OrderResponse             ←    Order
TradeResponse             ←    Trade
```

**Alternatives Considered:**
- Modify domain models to be Pydantic: Violates non-goal of no breaking changes
- Use dataclasses for API: Loses Pydantic validation features
- Direct serialization: Loses control over API representation

### Decision 3: Two-Step Workflow (Place vs Match)

**Choice:** Separate endpoints for `POST /orders` (place) and `POST /match` (execute)

**Rationale:**
- Educational value: observe order book state before matching
- Backtesting: control exactly when matching occurs
- Mirrors conceptual separation in trading systems
- Enables inspection between placement and execution

**Workflow:**
```
POST /orders  →  [order book updated, no matching]
GET /orders   →  [inspect current state]
POST /match   →  [execute matching at specified timestamp]
GET /trades   →  [view execution results]
```

**Alternatives Considered:**
- Auto-match on placement: Hides matching logic, reduces educational value
- Single endpoint with flag: Less RESTful, muddies semantics
- Batch match endpoint with orders: Mirrors library but loses inspection point

### Decision 4: Client-Controlled IDs and Timestamps

**Choice:** Clients provide `order_id`, `timestamp` fields in requests

**Rationale:**
- Backtesting requires deterministic timestamps (not server time)
- Enables testing with specific time sequences
- Clients can ensure ID uniqueness in their domain
- Server validates but doesn't generate

**Validation:**
- Reject duplicate order IDs with 400 error
- Accept any timestamp (no server time comparison)
- Accept any string for IDs (no format requirements)

**Alternatives Considered:**
- Server-generated IDs: Breaks backtesting reproducibility
- Server timestamps: Prevents historical simulation
- Hybrid: Adds complexity without clear benefit

### Decision 5: Endpoint Structure

**Endpoints:**
```
POST   /orders          Place batch of orders (no matching)
POST   /match           Trigger matching with timestamp
GET    /orders          Get current order book state
GET    /trades          Get all executed trades (optional timestamp filter)
DELETE /orders/{id}     Cancel specific order
POST   /reset           Reset engine state (optional seed)
GET    /summary         Order book summary (aggregated levels)
```

**Rationale:**
- RESTful resource-oriented design
- Clear verb semantics (POST = action, GET = query)
- Batch support where valuable (orders placement)
- Single-item for operations that don't benefit from batching (cancel)

**Error Handling:**
- 400 for invalid requests (validation errors, duplicate IDs)
- 404 for cancel of non-existent order
- 422 for business logic violations (if any emerge)
- 500 for unexpected errors

### Decision 6: Package Structure

**Structure:**
```
src/order_matching/
├─ api/
│  ├─ __init__.py
│  ├─ app.py              # FastAPI app creation
│  ├─ routes.py           # Endpoint definitions
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ requests.py      # Pydantic request models
│  │  ├─ responses.py     # Pydantic response models
│  │  └─ converters.py    # Domain ↔ API conversion
│  └─ dependencies.py     # FastAPI dependencies (get engine)
```

**Rationale:**
- Nested under `api/` to clearly separate from core library
- Single `routes.py` sufficient for 7 endpoints
- `models/` subpackage for request/response schemas
- `converters.py` centralizes bidirectional mapping logic
- `dependencies.py` for FastAPI dependency injection patterns

### Decision 7: Testing Strategy

**Approach:** Use FastAPI's `TestClient` for integration tests

**Structure:**
```
tests/test_api/
├─ test_place_orders.py
├─ test_match.py
├─ test_get_orders.py
├─ test_get_trades.py
├─ test_cancel_order.py
├─ test_reset.py
├─ test_summary.py
└─ conftest.py           # Fixtures for TestClient
```

**Coverage:**
- Happy path: successful operations
- Error cases: validation failures, duplicates, not found
- State transitions: place → match → query workflows
- Edge cases: empty book, partial fills, expirations

**Rationale:**
- TestClient provides synchronous HTTP testing without running server
- Integration tests cover request → handler → domain → response
- Mirrors existing test structure (one file per module)

## Risks / Trade-offs

**Risk: No Concurrency Safety**
- **Impact:** Concurrent requests could corrupt MatchingEngine state
- **Mitigation:** Document as single-user demo tool, out of scope for production
- **Accepted:** Educational use case doesn't require concurrent users

**Risk: No Persistence**
- **Impact:** Server restart loses all state
- **Mitigation:** Provide reset endpoint for clean starts, document in-memory nature
- **Accepted:** Demo/backtesting scenarios typically run to completion

**Risk: Large Order Books → Memory Issues**
- **Impact:** Thousands of orders could exhaust memory
- **Mitigation:** Document as educational tool with reasonable limits
- **Accepted:** Demos use small order counts, not production scale

**Risk: No API Versioning**
- **Impact:** Future changes could break clients
- **Mitigation:** This is v1, can add `/v1/` prefix later if needed
- **Accepted:** Internal/educational tool doesn't require strict versioning yet

**Risk: Pydantic Conversion Overhead**
- **Impact:** Request → domain → response conversion adds latency
- **Mitigation:** Acceptable for demo use case, not high-frequency trading
- **Accepted:** Correctness and clarity over performance for education

**Trade-off: Two Endpoints vs One**
- **Gain:** Clear separation, educational value, inspection points
- **Cost:** Two round-trips instead of one for place-and-match
- **Accepted:** Use case prioritizes understanding over latency

## Migration Plan

**Deployment:**
1. Add new `src/order_matching/api/` package (no changes to existing code)
2. Update documentation with API usage examples
3. No migration needed (additive only)

**Rollback:**
- Simply don't use the API package
- Core library unaffected
- No data to migrate

**Compatibility:**
- Fully backward compatible
- Existing library users see no changes
- Optional API layer for those who want it

## Open Questions

None - design is fully specified based on confirmed requirements.
