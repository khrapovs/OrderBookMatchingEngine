# Spec: Market Simulation Frontend & API Integration

## Objective
Integrate the Python-based market simulation (`src/order_matching/simulation`) into the FastAPI server and HTML/JS frontend dashboard. This integration makes a small, hardcoded pool of simulated noise traders always active in the background, allowing users to manually place and cancel orders and observe matching executed against the automated agents in real-time.

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, Pydantic v2
- **Frontend**: HTML5, Vanilla CSS, Vanilla JavaScript (ES6 Modules)
- **Dependency/Package Manager**: uv

## Commands
- **Dev (FastAPI server)**: `uv run fastapi dev`
- **Test**: `uv run pytest`
- **Format / Lint**: `uv run prek run -v --show-diff-on-failure --all-files`

## Project Structure
The integration touches the following existing paths in the workspace:
- `src/order_matching/simulation/market.py` → Orchestrator class for simulation ticks
- `src/order_matching/api/app.py` → FastAPI application initialization and state
- `src/order_matching/api/utils.py` → Helper utilities for market setup
- `src/order_matching/api/routes/match.py` → Endpoint `/match` to step the market simulation
- `src/order_matching/api/routes/reset.py` → Endpoint `/reset` to reinitialize the market simulation
- `src/order_matching/api/static/index.html` → Dashboard HTML structure (reset modal changes)
- `src/order_matching/api/static/app.js` → Frontend application logic (tick management, reset calls)

## Code Style
- **Python**: Follow pep8/Ruff conventions. Class members must be private (prefixed with `_`) unless explicitly required by external components. Public properties should be used to expose read-only attributes.
  ```python
  class Market:
      def __init__(self, *, traders: list[BaseTrader], news_feed: NewsFeed, seed: int | None = None) -> None:
          self._engine = MatchingEngine(seed=seed)
          ...

      @property
      def engine(self) -> MatchingEngine:
          """The underlying matching engine."""
          return self._engine
  ```
- **JavaScript**: Use modern ES6 modules. Handle API calls using async/await with clean separation of UI rendering and data fetching.

## Testing Strategy
- **Framework**: `pytest`
- **Location**: Unit and integration tests live in the `tests/` folder.
- **Rules**:
  - Test suites must not access private properties of classes (e.g. `_engine` or `_traders`).
  - Add tests validating that the API routes correctly instantiate `Market` and trigger simulation steps during `/match` and `/reset` cycles.

## Boundaries
- **Always**:
  - Run formatting and checkers via `uv run prek` before committing.
  - Keep internal state private where possible.
- **Ask first**:
  - Changing the structure of existing REST endpoints.
  - Adding new dependencies to `pyproject.toml`.
- **Never**:
  - Access private properties (prefixed with `_`) inside tests.
  - Commit secrets, logs, or cache files to the repository.

## Success Criteria
- **Simulated Orders**: The backend's noise traders automatically submit orders at random intervals, which appear in the UI's aggregated order book, depth chart, and outstanding orders tables.
- **Manual Order Placement**: The user can place BUY or SELL limit/market orders from the UI, matching against active noise trader orders when prices overlap.
- **Engine Control (Pause/Resume)**: Clicking the "Engine Online" button successfully stops/resumes the auto-matching polling timer on the frontend, ensuring no simulated trader orders are placed or matched when paused.
- **Clean Reset**: Clicking "Reset Market" completely clears the order book. All subsequent orders are generated organically by the noise traders from scratch starting at the base reference price (100.0). The "Prepopulate order book..." checkbox is removed from the UI.

## Open Questions
None. All requirements, including the behavior of the reset modal and scope constraints, have been aligned during the initial interview.
