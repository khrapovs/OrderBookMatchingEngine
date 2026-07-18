from datetime import datetime

from order_matching.orders import Orders
from order_matching.simulation.market import Market
from order_matching.simulation.market_view import MarketView
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.traders.base import BaseTrader
from order_matching.simulation.traders.noise import NoiseTrader


# Create two custom traders that place crossing orders at a specific tick
class Buyer(BaseTrader):
    def place(self, *, market_view: MarketView, timestamp: datetime) -> Orders | None:  # noqa: ARG002
        from order_matching.enums import Side
        from order_matching.order import LimitOrder
        from order_matching.orders import Orders

        o = LimitOrder(
            side=Side.BUY, price=100.0, size=5.0, timestamp=timestamp, order_id="buy_1", trader_id=self.trader_id
        )
        return Orders([o])


class Seller(BaseTrader):
    def place(self, *, market_view: MarketView, timestamp: datetime) -> Orders | None:  # noqa: ARG002
        from order_matching.enums import Side
        from order_matching.order import LimitOrder
        from order_matching.orders import Orders

        o = LimitOrder(
            side=Side.SELL, price=100.0, size=5.0, timestamp=timestamp, order_id="sell_1", trader_id=self.trader_id
        )
        return Orders([o])


def test_market_orchestration_basic() -> None:
    # Set up news feed and traders
    feed = NewsFeed()
    trader_1 = NoiseTrader(trader_id="t1", average_arrival_interval=1.0, price_std_dev=0.5, size_params=(1, 5), seed=10)
    trader_2 = NoiseTrader(trader_id="t2", average_arrival_interval=1.0, price_std_dev=0.5, size_params=(1, 5), seed=20)

    market = Market(traders=[trader_1, trader_2], news_feed=feed, seed=42)

    assert len(market.view.executed_trades) == 0

    t1 = datetime(2023, 1, 1, 12, 0, 0)
    trades = market.step(t1)

    # On step 1, both traders should place orders since next_trade_time is None.
    # Check that they were placed in matching engine.
    assert len(market.view.bids_depth) > 0 or len(market.view.asks_depth) > 0
    assert len(market.view.executed_trades) == len(trades)


def test_market_crossing_trades() -> None:
    market = Market(traders=[Buyer("buyer"), Seller("seller")], news_feed=NewsFeed())
    t0 = datetime(2023, 1, 1, 10, 0)

    trades = market.step(t0)

    # They cross at 100.0, so 1 trade should execute
    assert len(trades) == 1
    assert trades[0].price == 100.0
    assert trades[0].size == 5.0
    assert len(market.view.executed_trades) == 1


def run_simulation(seed: int) -> list[float]:
    trader_1 = NoiseTrader(
        trader_id="t1", average_arrival_interval=2.0, price_std_dev=1.0, size_params=(1, 10), seed=seed
    )
    trader_2 = NoiseTrader(
        trader_id="t2", average_arrival_interval=2.0, price_std_dev=1.0, size_params=(1, 10), seed=seed + 1
    )
    market = Market(traders=[trader_1, trader_2], news_feed=NewsFeed(), seed=seed + 2)

    prices = []
    for i in range(10):
        t = datetime(2023, 1, 1, 10, 0, i)
        trades = market.step(t)
        prices.extend([tr.price for tr in trades])
    return prices


def test_market_determinism() -> None:
    prices_1 = run_simulation(42)
    prices_2 = run_simulation(42)
    prices_3 = run_simulation(99)

    assert prices_1 == prices_2
    # Different seeds should produce different outputs (highly likely)
    if len(prices_1) > 0 and len(prices_3) > 0:
        assert prices_1 != prices_3


def test_market_view_updates_during_simulation() -> None:
    market = Market(traders=[Buyer("buyer"), Seller("seller")], news_feed=NewsFeed())

    # Assert initial proxy state is empty
    assert market.view.last_trade_price is None
    assert len(market.view.bids_depth) == 0
    assert len(market.view.asks_depth) == 0

    # Step the simulation, triggering a trade crossing
    t0 = datetime(2023, 1, 1, 10, 0)
    market.step(t0)

    # Prove that MarketView automatically reflects the changes
    assert market.view.last_trade_price == 100.0
