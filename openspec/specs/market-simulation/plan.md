# Implementation Plan: Market Simulation MVP

## Overview
Implement a tick-based market simulation containing a fixed set of traders (specifically noise traders) that interact with the matching engine, observe the market state via a read-only proxy, and submit orders.

## Architecture Decisions
- **`MarketView` Proxy**: A dedicated proxy class to protect the matching engine's internals from direct trader manipulation. It wraps `MatchingEngine` and `NewsFeed` to expose only read-only methods and aggregates.
- **Poisson Process Arrival**: Noise traders use an exponential distribution (Poisson process) to compute their next random trade timestamp. They remain idle on ticks where `current_time < next_trade_time`.
- **Random State Source**: All random generators are initialized via the `get_random_generator` function defined in `src/order_matching/random.py`.
- **Discrete Step Loop**: A simple synchronous loop (`Market.step()`) advances simulation time. On each step, it runs the traders' `place()` method synchronously, then matches the resulting orders batch-by-batch in the matching engine.

## Task List

### Phase 1: Foundation & Base Structure
- [ ] **Task 1: NewsFeed & NewsEvent Models**
  - Define structured news event schema and a feed container to manage/retrieve events by simulation timestamp.
  - Implement tests in `tests/test_simulation/test_news_feed.py`.
- [ ] **Task 2: MarketView Proxy**
  - Implement the read-only wrapper around `MatchingEngine` and `NewsFeed` to provide summary statistics and news feed access.
  - Implement tests in `tests/test_simulation/test_market_view.py`.

### Checkpoint: Foundation
- [ ] Foundation components build successfully and all unit tests in `tests/test_simulation/` pass.

### Phase 2: Traders & Core Simulation
- [ ] **Task 3: BaseTrader Interface**
  - Implement the abstract `BaseTrader` class specifying `place(market_view, timestamp) -> Orders | None`.
  - Implement tests in `tests/test_simulation/test_base_trader.py`.
- [ ] **Task 4: NoiseTrader Implementation**
  - Build `NoiseTrader` subclass implementing exponential arrival rate intervals (Poisson process) and limit order price/size distribution.
  - Randomization is handled via `get_random_generator()`.
  - Implement tests in `tests/test_simulation/test_noise_trader.py`.
- [ ] **Task 5: Market Orchestrator**
  - Build the main `Market` class runner that manages the fixed trader list, news feed, matching engine, tick loop, and trade logging.
  - Implement tests in `tests/test_simulation/test_market.py`.

### Checkpoint: Core Features
- [ ] Full simulation runs end-to-end; traders place orders and they are successfully matched by `Market`.

### Phase 3: Quality Checks & Polish
- [ ] **Task 6: Verification and Formatting**
  - Run the entire simulation test suite under `tests/test_simulation/` and run `prek` quality/formatting checks across the codebase.

### Checkpoint: Complete
- [ ] All tests pass.
- [ ] Code is formatted and passes ruff linter via `prek`.
- [ ] Ready for human review.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Inactive traders causing loop overhead | Low | The `NoiseTrader` checks time-to-act in `O(1)` operations and returns early if idle. |
| Non-deterministic random generator | Medium | Initialize all random processes using `get_random_generator` with explicit seed configurations. |
| Direct write access to MatchingEngine | Medium | Rigorously audit `MarketView` interface to ensure no mutable state or underlying engine methods are exposed. |

## Open Questions
- None.
