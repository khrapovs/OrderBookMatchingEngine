# Implementation Plan: Market Simulation Frontend & API Integration

## Overview
This plan details the steps required to integrate the `Market` simulation class and its programmatic noise traders into the FastAPI web API and frontend dashboard. The engine's state will be wrapped in a simulation runner, making market noise traders continuously active, generating dynamic order book volume in real-time.

## Architecture Decisions
1. **Always-On Simulation**: The `app.state` will hold `app.state.market` (a `Market` instance containing the traders).
2. **Unified State Pointer**: `app.state.engine` will point to `app.state.market.engine`. This keeps all other existing routes (`/place`, `/orders`, `/summary`, `/cancel`) working out-of-the-box without rewriting their database-like dependencies, because they operate directly on the same underlying `MatchingEngine`.
3. **Discrete Ticks**: Instead of running background threads (which introduces race conditions with manual API calls and violates the educational single-user assumption of the server), simulated trader step ticks will run synchronous actions when `/match` is called. This perfectly matches the frontend's auto-matching loop, which calls `/match` every second.
4. **Clean Reset**: Resetting the market deletes the simulation state and starts a new one with a clean engine, letting noise traders build the order book from scratch.

## Task List

### Phase 1: Foundation
- [ ] Task 1: Expose engine property in Market
- [ ] Task 2: Create helper function to instantiate market with traders
- [ ] Task 3: Unit tests for market engine property and helper

### Checkpoint: Foundation
- [ ] Tests pass: `uv run pytest tests/test_simulation/`
- [ ] Code builds and conforms to `prek` checks

### Phase 2: API Integration
- [ ] Task 4: Initialize market and engine in app state
- [ ] Task 5: Refactor match endpoint to step the market simulation
- [ ] Task 6: Refactor reset endpoint to reinitialize the market simulation
- [ ] Task 7: Integration tests for API endpoints with simulation

### Checkpoint: API & Core Integration
- [ ] Mock server matching runs execute `market.step()` and return simulated trades.
- [ ] Mock reset clears server state and recreates `Market`.
- [ ] Run integration test suite: `uv run pytest tests/test_api/`

### Phase 3: Frontend Polish & Verification
- [ ] Task 8: Remove prepopulate checkbox from reset modal HTML
- [ ] Task 9: Update frontend JS app reset logic
- [ ] Task 10: Run formatting and linting checks

### Checkpoint: Complete
- [ ] All tests pass: `uv run pytest`
- [ ] Dashboard is visually verified using a web browser:
  - Noise traders place orders continuously.
  - Manual orders match against noise traders.
  - Reset modal seed functionality works.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| **Thread Safety / Race Conditions** | Medium | Use synchronous discrete steps in `/match` endpoint rather than running a background background loop. |
| **Reset prepopulate code paths** | Low | Keep Pydantic models backward compatible by leaving `prepopulate` field but ignoring it in backend logic. |
| **Lack of initial orders (cold start)** | Low | The noise traders have small arrival intervals (e.g. 1.5s) and will populate the book within a few seconds of startup or reset. |

## Open Questions
None.
