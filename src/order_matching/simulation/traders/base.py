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

    def place(self, *, market_view: MarketView, timestamp: datetime) -> Orders | None:
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
