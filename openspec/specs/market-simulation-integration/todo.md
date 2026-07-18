# Tasks: Market Simulation Integration

## Task 1: Expose engine property in Market

**Description:** Add a public property getter `engine` to the `Market` class in `src/order_matching/simulation/market.py` that returns the underlying `MatchingEngine` instance (`_engine`). This allows API routes to interact with the engine.

**Acceptance criteria:**
- [ ] `Market` has `@property def engine(self) -> MatchingEngine` property.
- [ ] Returns `self._engine`.

**Verification:**
- [ ] Code syntax is correct.

**Dependencies:** None

**Files likely touched:**
- `src/order_matching/simulation/market.py`

**Estimated scope:** XS

---

## Task 2: Create helper function to instantiate market with traders

**Description:** Create a helper function `create_market(seed: int | None = None) -> Market` in `src/order_matching/api/utils.py`. The function initializes a `Market` with three `NoiseTrader`s with hardcoded realistic parameters (e.g. noise_fast with average interval 1.5s, noise_medium with average interval 3.0s, noise_slow with average interval 6.0s), an empty `NewsFeed()`, and passes the `seed` parameter down.

**Acceptance criteria:**
- [ ] `create_market` function is exported from `src/order_matching/api/utils.py`.
- [ ] It creates and returns a `Market` instance with the three defined noise traders.
- [ ] The seed parameter is propagated correctly.

**Verification:**
- [ ] Import and invoke helper in a Python shell or test, verifying it returns a `Market` instance.

**Dependencies:** None

**Files likely touched:**
- `src/order_matching/api/utils.py`

**Estimated scope:** XS

---

## Task 3: Unit tests for market engine property and helper

**Description:** Add unit tests to verify the new property and helper function work as expected, without violating boundaries (e.g. do not access private attributes like `_traders` or `_engine` in tests).

**Acceptance criteria:**
- [ ] Test verifying `market.engine` is a `MatchingEngine` instance.
- [ ] Test verifying `create_market()` returns a valid `Market` instance.

**Verification:**
- [ ] Run pytest: `uv run pytest tests/test_simulation/`

**Dependencies:** Task 1, Task 2

**Files likely touched:**
- `tests/test_simulation/test_market.py` (or create a new test file under `tests/test_simulation/` if not existing)

**Estimated scope:** S

---

## Task 4: Initialize market and engine in app state

**Description:** Update `src/order_matching/api/app.py` to import `create_market` and use it to initialize `app.state.market`. Point `app.state.engine` to `app.state.market.engine`.

**Acceptance criteria:**
- [ ] FastAPI `app.state` has a `market` attribute holding the `Market` simulation orchestrator.
- [ ] FastAPI `app.state.engine` points to `app.state.market.engine`.

**Verification:**
- [ ] Start backend server: `uv run fastapi dev` (verifies it starts successfully).

**Dependencies:** Task 2

**Files likely touched:**
- `src/order_matching/api/app.py`

**Estimated scope:** XS

---

## Task 5: Refactor match endpoint to step the market simulation

**Description:** Modify the POST `/match` route handler in `src/order_matching/api/routes/match.py` to call `market.step(timestamp)` instead of `engine.match(timestamp)`. Note that `market.step(timestamp)` returns a `list[Trade]`, whereas `engine.match()` returns an `ExecutedTrades` container object. Update conversion and trade accumulation accordingly.

**Acceptance criteria:**
- [ ] `/match` endpoint calls `request.app.state.market.step(timestamp)`.
- [ ] Executes simulated traders' orders and matching.
- [ ] Returns trades in response body.
- [ ] Appends executed trades list to `request.app.state.trades`.

**Verification:**
- [ ] Call POST `/match` via curl / HTTP client and verify response shape.

**Dependencies:** Task 1, Task 4

**Files likely touched:**
- `src/order_matching/api/routes/match.py`

**Estimated scope:** S

---

## Task 6: Refactor reset endpoint to reinitialize the market simulation

**Description:** Modify the POST `/reset` route handler in `src/order_matching/api/routes/reset.py` to recreate a new `Market` instance using `create_market(seed=payload.seed)` and assign it to `app.state.market` and `app.state.engine`. The `payload.prepopulate` option should be ignored as the book starts empty.

**Acceptance criteria:**
- [ ] `/reset` endpoint reinitializes `request.app.state.market` and `request.app.state.engine` with a new market simulation.
- [ ] Correctly forwards the seed value.
- [ ] Resets `request.app.state.trades = []`.

**Verification:**
- [ ] Call POST `/reset` and verify market gets reset.

**Dependencies:** Task 2, Task 4

**Files likely touched:**
- `src/order_matching/api/routes/reset.py`

**Estimated scope:** S

---

## Task 7: Integration tests for API endpoints with simulation

**Description:** Add/update integration tests for the API routes in `tests/` directory to ensure that orders are placed, simulated traders step, and reset functions work as expected.

**Acceptance criteria:**
- [ ] API integration tests run successfully without failing.
- [ ] Test coverage for the Refactored `/match` and `/reset` endpoints.

**Verification:**
- [ ] Run pytest: `uv run pytest tests/`

**Dependencies:** Task 5, Task 6

**Files likely touched:**
- `tests/test_api/test_routes.py` (or equivalent API routing tests file)

**Estimated scope:** S

---

## Task 8: Remove prepopulate checkbox from reset modal HTML

**Description:** Remove the checkbox input with ID `reset-prepopulate` and its label and container elements from the `#reset-modal` in `src/order_matching/api/static/index.html`.

**Acceptance criteria:**
- [ ] No checkbox for prepopulation is visible or present in the reset modal DOM.

**Verification:**
- [ ] Inspect reset modal in the browser.

**Dependencies:** None

**Files likely touched:**
- `src/order_matching/api/static/index.html`

**Estimated scope:** XS

---

## Task 9: Update frontend JS app reset logic

**Description:** Update `src/order_matching/api/static/app.js` to remove references to the deleted prepopulate checkbox element, and call `handleReset` with `seed` and `false` (or omit prepopulate).

**Acceptance criteria:**
- [ ] Confirm reset button listener does not look up `#reset-prepopulate`.
- [ ] Correctly issues API reset calls to `/reset`.

**Verification:**
- [ ] Open UI, click Reset Market, verify in Chrome DevTools that the POST body to `/reset` does not depend on a prepopulate input.

**Dependencies:** Task 8

**Files likely touched:**
- `src/order_matching/api/static/app.js`

**Estimated scope:** S

---

## Task 10: Run formatting and linting checks

**Description:** Run formatters and style checkers to ensure code style is preserved and clean.

**Acceptance criteria:**
- [ ] Format and lint pass without failures.

**Verification:**
- [ ] Run command: `uv run prek run -v --show-diff-on-failure --all-files`

**Dependencies:** All previous tasks

**Files likely touched:**
- All files modified during integration.

**Estimated scope:** XS
