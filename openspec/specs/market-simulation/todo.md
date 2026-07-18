# Task Checklist: Market Simulation MVP

## Task 1: NewsFeed & NewsEvent Models

**Description:**
Implement the data structures to hold structured news events and query them by virtual timestamp.

**Acceptance criteria:**
- `NewsEvent` dataclass with `timestamp`, `headline`, and `impact` (numeric float or dict mapping asset parameters).
- `NewsFeed` class initialized with a list of `NewsEvent` objects, providing `get_news(timestamp)` which returns all news events with timestamps `<= timestamp`.

**Verification:**
- Run test: `uv run pytest tests/test_simulation/test_news_feed.py`

**Dependencies:** None

**Files likely touched:**
- `src/order_matching/simulation/news_feed.py`
- `src/order_matching/simulation/__init__.py`
- `tests/test_simulation/test_news_feed.py`

**Estimated scope:** Small (2 files)

---

## Task 2: MarketView Proxy

**Description:**
Implement the read-only wrapper around `MatchingEngine` and `NewsFeed` to provide access to summary market statistics and news history.

**Acceptance criteria:**
- `MarketView` wraps `MatchingEngine` and `NewsFeed`.
- Exposes read-only properties: `mid_price`, `spread`, `last_trade_price`, `bids_depth`, `asks_depth`.
- Exposes method `get_news(timestamp)` which delegates to the underlying `NewsFeed`.
- No mutating methods of the engine or news feed are exposed.

**Verification:**
- Run test: `uv run pytest tests/test_simulation/test_market_view.py`

**Dependencies:** Task 1

**Files likely touched:**
- `src/order_matching/simulation/market_view.py`
- `tests/test_simulation/test_market_view.py`

**Estimated scope:** Small (2 files)

---

## Checkpoint 1: Foundation
- News models and `MarketView` are implemented.
- Foundation unit tests pass.

---

## Task 3: BaseTrader Interface

**Description:**
Implement the base class that defines the common interface for all simulated traders.

**Acceptance criteria:**
- `BaseTrader` abstract/base class with constructor taking `trader_id`.
- Defines `place(market_view, timestamp) -> Orders | None` abstract method.

**Verification:**
- Run test: `uv run pytest tests/test_simulation/test_base_trader.py`

**Dependencies:** Task 2

**Files likely touched:**
- `src/order_matching/simulation/base_trader.py`
- `tests/test_simulation/test_base_trader.py`

**Estimated scope:** Small (2 files)

---

## Task 4: NoiseTrader Implementation

**Description:**
Implement the `NoiseTrader` that places random buy/sell limit orders at intervals determined by a Poisson process (exponentially distributed arrival times).

**Acceptance criteria:**
- Inherits `BaseTrader`.
- Takes `average_arrival_interval` (as float seconds or `timedelta`), `price_std_dev` (price deviation), `size_params` (e.g., uniform range or mean/std), and an optional random seed or generator.
- All random state logic is generated using a generator retrieved from `get_random_generator()`.
- Correctly implements scheduling: on step `t`, if `t >= next_trade_time`, places a buy/sell limit order around the current mid-price (or a base price if no mid-price exists) and schedules the next trade time. Otherwise, returns `None`.

**Verification:**
- Run test: `uv run pytest tests/test_simulation/test_noise_trader.py`

**Dependencies:** Task 3

**Files likely touched:**
- `src/order_matching/simulation/noise_trader.py`
- `tests/test_simulation/test_noise_trader.py`

**Estimated scope:** Small (2 files)

---

## Task 5: Market Orchestrator

**Description:**
Build the main simulation loop container (`Market`) that manages fixed traders, news feed, matching engine, tick progression, and trade logging.

**Acceptance criteria:**
- `Market` takes `traders: list[BaseTrader]`, `news_feed: NewsFeed`, and optional `MatchingEngine` and `seed` parameters.
- Uses `get_random_generator()` with `seed` for simulation random state initialization.
- `Market.step(timestamp)` advances virtual time, runs all traders to collect orders, places them, matches them, and logs executed trades.
- Exposes `executed_trades` log history.

**Verification:**
- Run test: `uv run pytest tests/test_simulation/test_market.py`

**Dependencies:** Task 4

**Files likely touched:**
- `src/order_matching/simulation/market.py`
- `tests/test_simulation/test_market.py`

**Estimated scope:** Small (2 files)

---

## Task 6: Verification and Formatting

**Description:**
Run the entire simulation test suite under `tests/test_simulation/` and perform prek quality/formatting checks.

**Acceptance criteria:**
- integrated tests pass successfully.
- Code matches existing conventions and linting rules.

**Verification:**
- Run: `uv run pytest tests/test_simulation/`
- Run: `uv run prek run -v --show-diff-on-failure --all-files`

**Dependencies:** Task 5

**Files likely touched:** None (verification task)

---

## Checkpoint 2: Final MVP Complete
- All simulation tests pass cleanly.
- Pre-commit rules run with zero warnings/errors.
