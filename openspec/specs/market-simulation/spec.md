# Spec: Market Simulation

## Objective
Implement a tick-based market simulation framework containing fixed set of traders (specifically noise traders) that interact with the matching engine, observe the market state via a read-only proxy, and submit orders, laying down a highly scalable and extensible architecture for future reactive trader types.

### User Stories & Use Cases
- **Simulation Runner**: As a developer, I can initialize a market simulation with a list of traders, run it tick-by-tick or in a loop, and examine the resulting order book and executed trade logs.
* **Base Trader**: As a base trader class, I can observe aggregate market statistics (spread, mid-price, last trade price, total depth) and news history, but I cannot modify the matching engine state directly.
* **Noise Trader**: As a noise trader, I place random buy or sell limit orders around the current market mid-price at random intervals determined by a Poisson process (exponentially distributed arrival times).
* **Market Engine**: As a market engine, I collect submitted orders from all traders on each tick, place them into the order book, trigger the matching engine, and record executions.

## Tech Stack
* **Language**: Python >= 3.11
* **Matching Engine**: Existing `order-matching` package core (`MatchingEngine`, `OrderBook`, `Orders`, `LimitOrder`)
* **Libraries**: `numpy` for random distributions (Poisson/exponential intervals, normal prices).

## Commands
* **Run Tests**: `uv run pytest tests/test_simulation.py`
* **Run Pre-Commit Checks**: `uv run prek run -v --show-diff-on-failure --all-files`

## Project Structure
The simulation module will be structured under a new subpackage `src/order_matching/simulation/`:
```text
src/order_matching/simulation/
├── __init__.py
├── base_trader.py       # BaseTrader class interface
├── noise_trader.py      # NoiseTrader implementation
├── market_view.py       # MarketView read-only proxy
├── news_feed.py         # NewsFeed and NewsEvent models
└── market.py            # Market runner managing the loop
tests/test_simulation/
├── __init__.py
├── test_base_trader.py  # tests for base trader
├── test_noise_trader.py # tests for noise trader
├── test_market_view.py  # tests for market view
├── test_news_feed.py    # tests for news feed
└── test_market.py       # tests for market
```

## Code Style
Code must use explicit type hints, follow PEP 8, and document classes/methods using NumPy docstring style (consistent with the rest of the repository).

```python
from datetime import datetime
from order_matching.orders import Orders
from order_matching.simulation.market_view import MarketView

class BaseTrader:
    """Base class for all simulated traders.

    Parameters
    ----------
    trader_id : str
        Unique identifier for the trader.
    """

    def __init__(self, trader_id: str) -> None:
        self.trader_id = trader_id

    def place(self, market_view: MarketView, timestamp: datetime) -> Orders | None:
        """Evaluate market state and news to return orders to be placed.

        Parameters
        ----------
        market_view : MarketView
            Read-only interface to poll market stats and news feed.
        timestamp : datetime
            Current simulation timestamp.

        Returns
        -------
        Orders | None
            Orders to place in the book, or None if idle.
        """
        raise NotImplementedError
```

## Testing Strategy
* **Framework**: `pytest`
* **Test Location**: `tests/test_simulation/`
* **Coverage Requirements**: 100% code coverage for the `simulation` package.
* **Test Cases**:
  1. **MarketView Read-Only Protection**: Verify that the matching engine cannot be directly modified or accessed in write mode via `MarketView`.
  2. **Noise Trader Scheduling**: Test that the noise trader correctly computes the next action time using an exponential distribution and remains idle until that time.
  3. **Determinism**: Verify that running the simulation with a fixed random seed produces identical sequences of orders and trades.
  4. **Loop Execution**: Run a full simulation loop for a set number of ticks and verify orders are submitted and matched.

## Boundaries
* **Always**:
  * Pass a shared/seeded `random.Random` or `numpy.random.Generator` instance to ensure deterministic simulation behavior (uses `get_random_generator` utility function).
  * Use the existing matching engine core components (e.g. `Orders`, `LimitOrder`, `Side`, `MatchingEngine`) without modifying them.
* **Ask first**:
  * Modifying existing matching engine APIs or core classes in `src/order_matching/matching_engine.py`.
* **Never**:
  * Expose write methods or private matching engine attributes directly through the `MarketView` proxy.

## Success Criteria
- [ ] `Market` correctly advances time tick-by-tick and aggregates trade logs.
- [ ] `NoiseTrader` places orders around mid-price using exponential arrival intervals.
- [ ] `MarketView` provides read-only stats (`mid_price`, `spread`, `last_trade_price`, aggregate bids/asks depth) and news feed query interface.
- [ ] Complete unit and integration test suite runs and passes.
- [ ] Pre-commit validation `prek` passes with no format or linting errors.

## Open Questions
- None. (All design decisions clarified in previous steps).
