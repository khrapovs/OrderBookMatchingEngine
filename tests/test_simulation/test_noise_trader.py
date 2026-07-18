from datetime import datetime

from order_matching.matching_engine import MatchingEngine
from order_matching.simulation.market_view import MarketView
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.noise_trader import NoiseTrader
from order_matching.trade import Trade


def test_noise_trader_initialization() -> None:
    trader = NoiseTrader(
        trader_id="noise_1",
        average_arrival_interval=1.0,
        price_std_dev=2.0,
        size_params=(1.0, 10.0),
        base_price=50.0,
        seed=123,
    )
    assert trader.trader_id == "noise_1"
    assert trader.average_arrival_interval == 1.0
    assert trader.price_std_dev == 2.0
    assert trader.size_params == (1.0, 10.0)
    assert trader.base_price == 50.0
    assert trader.next_trade_time is None


def test_noise_trader_place_logic() -> None:
    trader = NoiseTrader(
        trader_id="noise_1",
        average_arrival_interval=5.0,
        price_std_dev=1.0,
        size_params=(2.0, 4.0),
        base_price=10.0,
        seed=42,
    )
    engine = MatchingEngine()
    news = NewsFeed()
    executed_trades: list[Trade] = []
    view = MarketView(matching_engine=engine, news_feed=news, executed_trades=executed_trades)

    # First call must trigger trade
    t0 = datetime(2023, 1, 1, 10, 0)
    orders = trader.place(market_view=view, timestamp=t0)

    assert orders is not None
    assert len(orders) == 1
    order = list(orders)[0]
    assert order.trader_id == "noise_1"
    assert 2.0 <= order.size <= 4.0
    assert order.price > 0.0
    assert trader.next_trade_time is not None
    assert trader.next_trade_time > t0

    # Next call before time must return None
    t1 = datetime(2023, 1, 1, 10, 0, 1)
    assert trader.place(market_view=view, timestamp=t1) is None


def test_noise_trader_determinism() -> None:
    trader_1 = NoiseTrader(
        trader_id="noise_1", average_arrival_interval=2.0, price_std_dev=1.0, size_params=(1.0, 5.0), seed=42
    )
    trader_2 = NoiseTrader(
        trader_id="noise_1", average_arrival_interval=2.0, price_std_dev=1.0, size_params=(1.0, 5.0), seed=42
    )

    engine = MatchingEngine()
    news = NewsFeed()
    view = MarketView(matching_engine=engine, news_feed=news, executed_trades=[])

    t0 = datetime(2023, 1, 1, 10, 0)
    orders_1 = trader_1.place(market_view=view, timestamp=t0)
    orders_2 = trader_2.place(market_view=view, timestamp=t0)

    assert orders_1 is not None and orders_2 is not None
    o1 = list(orders_1)[0]
    o2 = list(orders_2)[0]

    assert o1.side == o2.side
    assert o1.price == o2.price
    assert o1.size == o2.size
    assert trader_1.next_trade_time == trader_2.next_trade_time
