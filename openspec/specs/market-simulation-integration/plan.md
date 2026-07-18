# Plan: Market Simulation Integration

This plan outlines the technical steps to integrate the market simulation with the API and frontend, using the specifications defined in `spec.md`.

## Key Components & Changes

### 1. Market class property (`market.py`)
- Modify `src/order_matching/simulation/market.py` to add `engine` property.

### 2. Market Setup & App State (`utils.py`, `app.py`)
- Define `create_market` helper function in `src/order_matching/api/utils.py`.
- Initialize `app.state.market` and `app.state.engine` in `src/order_matching/api/app.py`.

### 3. API Endpoints (`match.py`, `reset.py`)
- Update `/match` to use `market.step(timestamp)` and return executions.
- Update `/reset` to recreate the `Market` instance using `create_market(seed)`.

### 4. UI Dashboard updates (`index.html`, `app.js`)
- Remove prepopulation checkbox element from UI.
- Update javascript logic to no longer pass prepopulate flag.

## Risks & Mitigations
- **Noise Trader Speed**: If noise traders place orders too fast or slow, it might affect UI responsiveness or feel sluggish.
  - *Mitigation*: Hardcode realistic intervals (e.g., 1.5s, 3.0s, 6.0s) and keep the discrete step synchronous.
- **Unprocessed orders dependency**: Some endpoints might use `app.state.engine`. Since `market.engine` is a reference to the same engine, updating `app.state.engine = market.engine` prevents breaking these dependencies.
