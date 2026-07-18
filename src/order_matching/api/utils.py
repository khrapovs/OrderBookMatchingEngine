from datetime import datetime

from order_matching.enums import Side
from order_matching.matching_engine import MatchingEngine
from order_matching.order import LimitOrder
from order_matching.orders import Orders
from order_matching.simulation.market import Market
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.traders.noise import NoiseTrader


def create_market(seed: int | None = None) -> Market:
    """Create a market simulation with a small pool of noise traders."""
    traders = [
        NoiseTrader(
            trader_id="noise_fast",
            average_arrival_interval=1.5,
            price_std_dev=0.02,
            size_params=(1.0, 5.0),
            base_price=100.0,
            seed=seed,
        ),
        NoiseTrader(
            trader_id="noise_medium",
            average_arrival_interval=3.0,
            price_std_dev=0.05,
            size_params=(5.0, 15.0),
            base_price=100.0,
            seed=seed,
        ),
        NoiseTrader(
            trader_id="noise_slow",
            average_arrival_interval=6.0,
            price_std_dev=0.1,
            size_params=(10.0, 50.0),
            base_price=100.0,
            seed=seed,
        ),
    ]
    return Market(traders=traders, news_feed=NewsFeed(), seed=seed)


def prepopulate_engine(engine: MatchingEngine) -> MatchingEngine:
    """Prepopulate the matching engine with some initial non-crossing orders."""
    now = datetime.now()
    trader_id = "market_maker"
    orders = [
        # Bids (BUY)
        LimitOrder(side=Side.BUY, price=99.50, size=15.0, timestamp=now, order_id="init_buy_1", trader_id=trader_id),
        LimitOrder(side=Side.BUY, price=99.00, size=10.0, timestamp=now, order_id="init_buy_2", trader_id=trader_id),
        LimitOrder(side=Side.BUY, price=98.50, size=25.0, timestamp=now, order_id="init_buy_3", trader_id=trader_id),
        LimitOrder(side=Side.BUY, price=98.00, size=30.0, timestamp=now, order_id="init_buy_4", trader_id=trader_id),
        # Asks (SELL)
        LimitOrder(side=Side.SELL, price=100.50, size=12.0, timestamp=now, order_id="init_sell_1", trader_id=trader_id),
        LimitOrder(side=Side.SELL, price=101.00, size=8.0, timestamp=now, order_id="init_sell_2", trader_id=trader_id),
        LimitOrder(side=Side.SELL, price=101.50, size=22.0, timestamp=now, order_id="init_sell_3", trader_id=trader_id),
        LimitOrder(side=Side.SELL, price=102.00, size=28.0, timestamp=now, order_id="init_sell_4", trader_id=trader_id),
    ]
    engine.place(Orders(orders=orders))
    return engine
