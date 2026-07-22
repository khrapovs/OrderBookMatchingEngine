# Purpose

Provides a FastAPI REST API layer for remote order book matching engine control, order placement, matching triggers, state queries, and serves a modern interactive web dashboard UI.

# Ownership

Owns REST API routes, request/response models, dependencies, utilities, and static frontend assets.

# Local Contracts

**Structure:**
- `app.py` - FastAPI application entry point, middleware, static file mounting
- `routes/` - API endpoint handlers (place, match, get_orders, get_trades, cancel_order, reset, summary, root)
- `models/` - Pydantic request/response models and converters to/from core domain objects
- `dependencies.py` - FastAPI dependency injection (shared matching engine state)
- `utils.py` - API utilities (currently simulation state management)
- `static/` - Frontend SPA assets (HTML, CSS, JS) for interactive dashboard

**API Contract:**
- Single in-memory matching engine instance shared across requests (not thread-safe, educational use only)
- POST endpoints modify state; GET endpoints read state
- No persistence layer (restart clears state)
- Interactive docs at `/docs`

# Work Guidance

- Keep route handlers thin: validate input, call core engine methods, convert to response models
- Use Pydantic models for all request/response validation
- Converters in `models/converters.py` translate between API models and core domain objects
- Engine state injected via `get_matching_engine` dependency
- Frontend code in `static/` is separate from API logic

# Verification

```shell
uv run pytest tests/test_api/
```

# Child DOX Index

None - flat structure sufficient for current API complexity.
