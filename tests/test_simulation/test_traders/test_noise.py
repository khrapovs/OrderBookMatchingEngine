from datetime import datetime

from order_matching.matching_engine import MatchingEngine
from order_matching.simulation.market_view import MarketView
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.traders.noise import NoiseTrader


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

    # Verify state initialization by testing place behavior
    engine = MatchingEngine()
    news = NewsFeed()
    view = MarketView(order_book=engine.unprocessed_orders, news_feed=news)
    orders = trader.place(market_view=view, timestamp=datetime(2023, 1, 1, 10, 0))
    assert orders is not None
    assert len(orders) == 1


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
    view = MarketView(order_book=engine.unprocessed_orders, news_feed=news)

    # First call must trigger trade
    t0 = datetime(2023, 1, 1, 10, 0)
    orders = trader.place(market_view=view, timestamp=t0)

    assert orders is not None
    assert len(orders) == 1
    order = list(orders)[0]
    assert order.trader_id == "noise_1"
    assert 2.0 <= order.size <= 4.0
    assert order.price > 0.0

    # Next call shortly after (e.g. 1 millisecond) must return None (idle state)
    t1 = datetime(2023, 1, 1, 10, 0, 0, 1000)
    assert trader.place(market_view=view, timestamp=t1) is None

    # Verify it acts again if we jump far ahead in time (e.g. 100 seconds later)
    t2 = datetime(2023, 1, 1, 10, 1, 40)
    assert trader.place(market_view=view, timestamp=t2) is not None


def test_noise_trader_determinism() -> None:
    trader_1 = NoiseTrader(
        trader_id="noise_1", average_arrival_interval=2.0, price_std_dev=1.0, size_params=(1.0, 5.0), seed=42
    )
    trader_2 = NoiseTrader(
        trader_id="noise_1", average_arrival_interval=2.0, price_std_dev=1.0, size_params=(1.0, 5.0), seed=42
    )

    engine = MatchingEngine()
    news = NewsFeed()
    view = MarketView(order_book=engine.unprocessed_orders, news_feed=news)

    t0 = datetime(2023, 1, 1, 10, 0)
    orders_1 = trader_1.place(market_view=view, timestamp=t0)
    orders_2 = trader_2.place(market_view=view, timestamp=t0)

    assert orders_1 is not None and orders_2 is not None
    o1 = list(orders_1)[0]
    o2 = list(orders_2)[0]

    assert o1.side == o2.side
    assert o1.price == o2.price
    assert o1.size == o2.size

    # Verify both remain idle at the exact same intermediate timestamp
    t_mid = datetime(2023, 1, 1, 10, 0, 0, 1000)
    assert trader_1.place(market_view=view, timestamp=t_mid) is None
    assert trader_2.place(market_view=view, timestamp=t_mid) is None

    # Verify both place orders at a later identical timestamp
    t_far = datetime(2023, 1, 1, 10, 1, 0)
    o1_later = trader_1.place(market_view=view, timestamp=t_far)
    o2_later = trader_2.place(market_view=view, timestamp=t_far)
    assert o1_later is not None and o2_later is not None
    assert list(o1_later)[0].price == list(o2_later)[0].price
