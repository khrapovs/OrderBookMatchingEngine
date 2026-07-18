# Market Simulation MVP (Tick-Loop & MarketView Proxy)

## Problem Statement
How might we design a modular, tick-based market simulation architecture where diverse trader classes (starting with polling-based noise traders) can observe market summary statistics and place orders on discrete ticks, ensuring the architecture remains clean, testable, and highly extensible for future news-reactive and interactive frontend use cases?

## Recommended Direction
We will implement a synchronous, tick-based simulation (`Market`) where time is advanced in discrete intervals (e.g. 1 second or 1 tick). The market maintains:
1. An underlying `MatchingEngine` instance.
2. A `NewsFeed` that holds current and historic news events.
3. A `MarketView` proxy class, which provides read-only access to market statistics (spread, mid-price, last trade price, total depth) and news history, protecting the simulation from direct trader manipulation.

On every simulation step:
1. The `Market` advances virtual time by `dt`.
2. The `Market` updates any active news events for that tick.
3. The `Market` iterates through all registered `BaseTrader` customers, invoking `trader.place(market_view, current_time)`.
4. A trader returns an `Orders` object containing one or more orders to be placed, or `None` if they choose to remain idle.
5. Inactive traders check `current_time >= self.next_trade_time` to decide whether to act, keeping the check extremely lightweight.
6. The `Market` collects all orders, places them into the `MatchingEngine`, executes matching, and logs the executed trades.

## Key Assumptions to Validate
- [x] **Polling adequacy**: That polling `MarketView` summary stats once per tick is sufficient for noise traders and future news-based traders.
- [x] **Performance of idle loops**: That iterating through idle traders on every tick is performant enough for simple simulations (up to hundreds of traders).
- [x] **Deterministic behavior**: That the simulation remains fully reproducible given a random seed passed to both the engine and the traders.

## MVP Scope

### In Scope
- **Trader Initialization**: The trader list is fixed at initialization of the `Market` class.
- **Poisson Process Arrival**: Noise trader intervals (time between orders) are modeled as exponential random variables (Poisson process) using a configured fixed average arrival rate.
- **Random State Generation**: All random number generation uses the `get_random_generator` function in `src/order_matching/random.py`.
- `BaseTrader` interface with `place(market_view, timestamp) -> Orders | None`.
- `MarketView` read-only proxy exposing:
  - `mid_price`, `spread`, `last_trade_price`, `bids_depth`, `asks_depth` (summary stats from `MatchingEngine`).
  - `get_news(timestamp)` (polling from news generator).
- `NoiseTrader` extending `BaseTrader` that places random buy/sell limit orders around the mid-price at random intervals.
- `NewsFeed` supporting simple structured news events (e.g., impact, timestamp, headline).
- `Market` runner class that manages the main tick loop, customer list, order ingestion, matching invocation, and logging.
- **Test File Layout**: Unit and integration tests organized in the `tests/test_simulation/` directory with one test file per implementation file.

### Out of Scope / Not Doing (and Why)
- **Asynchronous/Multi-threaded Runner**: Avoids race conditions and locking overhead. Keeps the MVP simple and deterministic.
- **WebSocket/FastAPI endpoints for live streaming**: We will first design the core simulation engine. Exposing it to FastAPI can be done easily in a follow-up step.
- **Complex news-parsing NLP models**: Traders will poll simple structured news objects with numeric impact indicators (e.g., +10% demand shift) rather than parsing raw text.
