from datetime import datetime, timedelta

from order_matching.order import LimitOrder
from order_matching.orders import Orders
from order_matching.random import get_faker, get_random_generator
from order_matching.side import Side
from order_matching.simulation.base_trader import BaseTrader
from order_matching.simulation.market_view import MarketView


class NoiseTrader(BaseTrader):
    """Traded class that submits random limit orders at random intervals.

    Parameters
    ----------
    trader_id : str
        Unique identifier for the trader.
    average_arrival_interval : float
        The average arrival time between trades, in seconds (scale parameter).
    price_std_dev : float
        The standard deviation of the price offset relative to the reference price.
    size_params : tuple[float, float]
        The minimum and maximum size for generated orders.
    base_price : float, optional
        The default reference price to use when the order book has no mid-price.
    seed : int, optional
        Random seed for reproducibility.
    """

    def __init__(
        self,
        *,
        trader_id: str,
        average_arrival_interval: float,
        price_std_dev: float,
        size_params: tuple[float, float],
        base_price: float = 100.0,
        seed: int | None = None,
    ) -> None:
        super().__init__(trader_id=trader_id)
        self._average_arrival_interval = average_arrival_interval
        self._price_std_dev = price_std_dev
        self._size_params = size_params
        self._base_price = base_price
        self._rng = get_random_generator(seed=seed)
        self._faker = get_faker(seed=seed)
        self._next_trade_time: datetime | None = None

    def place(self, *, market_view: MarketView, timestamp: datetime) -> Orders | None:
        """Submit a random order if the scheduled action time is reached.

        Parameters
        ----------
        market_view : MarketView
            Read-only proxy to poll market status and news feed.
        timestamp : datetime
            Current simulation timestamp.

        Returns
        -------
        Orders | None
            A new batch containing a single limit order, or None if idle.
        """
        if self._next_trade_time is None:
            self._next_trade_time = timestamp

        if timestamp < self._next_trade_time:
            return None

        side = Side.BUY if self._rng.random() < 0.5 else Side.SELL
        mid = market_view.mid_price
        ref_price = mid if mid is not None else self._base_price

        price = self._rng.lognormal(mean=ref_price, sigma=self._price_std_dev)
        size = max(0.01, round(self._rng.uniform(*self._size_params), 2))
        order_id = f"{self.trader_id}_{self._faker.uuid4()}"

        order = LimitOrder(
            side=side, price=price, size=size, timestamp=timestamp, order_id=order_id, trader_id=self.trader_id
        )

        # Schedule next trade time
        delay_seconds = self._rng.exponential(self._average_arrival_interval)
        self._next_trade_time = timestamp + timedelta(seconds=delay_seconds)

        return Orders([order])
