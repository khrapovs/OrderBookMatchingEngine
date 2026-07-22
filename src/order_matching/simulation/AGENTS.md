# Purpose

Implements a discrete-time market simulation framework with automated trading agents, event-driven news feed, and read-only market view proxy for agent decision-making.

# Ownership

Owns simulation orchestration, trader framework, market view abstraction, and news feed event system.

# Local Contracts

**Components:**
- `market.py` - Main simulation orchestrator managing state transitions, registered traders, news feed integration
- `market_view.py` - Read-only proxy wrapper exposing market state to traders without direct matching engine access
- `news_feed.py` - Event-driven news feed with scheduled events triggering trader reactions
- `traders/` - Trading agent implementations (base class + concrete traders like NoiseTrader)

**Simulation Flow:**
1. Register traders with market
2. Configure news feed events (optional)
3. Step through discrete time periods
4. Each step: traders observe market → place orders → trigger matching
5. State-passing design: market state flows through simulation steps

# Work Guidance

- Traders receive `MarketView` proxy, never direct `MatchingEngine` access
- Poisson arrival processes model realistic order timing (NoiseTrader)
- News feed events can trigger sudden trader behavior changes
- All traders inherit from `BaseTrader` protocol/abstract base
- Simulation integrates with API for live dashboard updates

# Verification

```shell
uv run pytest tests/test_simulation/
```

# Child DOX Index

None - current structure is clear and contained.
