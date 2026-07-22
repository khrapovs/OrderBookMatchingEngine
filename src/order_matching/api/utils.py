from order_matching.simulation.market import Market
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.traders.base import BaseTrader
from order_matching.simulation.traders.noise import NoiseTrader


def create_market(*, seed: int | None = None, traders: list[BaseTrader] | None = None) -> Market:
    """Create a market simulation with a small pool of noise traders."""
    if traders is None:
        traders = [
            NoiseTrader(
                trader_id="noise_fast",
                average_arrival_interval=1.5,
                price_std_dev=0.002,
                size_params=(1.0, 5.0),
                base_price=100.0,
                seed=seed,
            ),
            NoiseTrader(
                trader_id="noise_medium",
                average_arrival_interval=3.0,
                price_std_dev=0.005,
                size_params=(5.0, 15.0),
                base_price=100.0,
                seed=seed,
            ),
            NoiseTrader(
                trader_id="noise_slow",
                average_arrival_interval=6.0,
                price_std_dev=0.01,
                size_params=(10.0, 50.0),
                base_price=100.0,
                seed=seed,
            ),
        ]
    return Market(traders=traders, news_feed=NewsFeed(), seed=seed)
