# TODO: Market Simulation Integration Tasks

- [ ] Task: Expose engine in Market class
  - Acceptance: `Market` class has a public `engine` property returning its underlying `MatchingEngine`.
  - Verify: Run unit tests / verify property exists.
  - Files: `src/order_matching/simulation/market.py`

- [ ] Task: Create helper function to instantiate market with traders
  - Acceptance: `create_market(seed: int | None = None) -> Market` creates a `Market` with three hardcoded noise traders (`noise_fast`, `noise_medium`, `noise_slow`).
  - Verify: Invoke function, assert returned value is a `Market` containing the traders.
  - Files: `src/order_matching/api/utils.py`

- [ ] Task: Initialize market and engine in app state
  - Acceptance: `app.state.market` holds the initialized `Market` instance, and `app.state.engine` points to its underlying engine.
  - Verify: Start FastAPI server and check that it launches.
  - Files: `src/order_matching/api/app.py`

- [ ] Task: Update match endpoint
  - Acceptance: `/match` route calls `market.step(timestamp)` to process simulated trader orders and trigger matching.
  - Verify: Invoke endpoint with a timestamp and check response has trade results.
  - Files: `src/order_matching/api/routes/match.py`

- [ ] Task: Update reset endpoint
  - Acceptance: `/reset` route reinitializes the market simulation with a new `Market` instance, optionally using a seed.
  - Verify: Call `/reset` and observe that the engine is reset.
  - Files: `src/order_matching/api/routes/reset.py`

- [ ] Task: Remove prepopulate checkbox from reset modal
  - Acceptance: The "Prepopulate order book..." checkbox is removed from the HTML markup in the reset modal.
  - Verify: Inspect the reset modal on the webpage.
  - Files: `src/order_matching/api/static/index.html`

- [ ] Task: Update frontend JS reset handler
  - Acceptance: The frontend reset button confirms and calls the reset API passing `prepopulate = false`.
  - Verify: Reset market via UI and check network request payload.
  - Files: `src/order_matching/api/static/app.js`

- [ ] Task: Run formatters and test suite
  - Acceptance: All formatting checks and existing test suites pass.
  - Verify: `uv run prek run -v --show-diff-on-failure --all-files` and `uv run pytest` succeed.
  - Files: all touched files
