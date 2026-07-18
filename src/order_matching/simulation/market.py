from datetime import datetime

from order_matching.matching_engine import MatchingEngine
from order_matching.simulation.market_view import MarketView
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.traders.base import BaseTrader
from order_matching.trade import Trade


class Market:
    """Orchestrates the market simulation tick loop, traders, and matching engine.

    Parameters
    ----------
    traders : list[BaseTrader]
        Fixed list of simulated traders participating in the market.
    news_feed : NewsFeed
        The news feed where macro/micro events are published.
    matching_engine : MatchingEngine, optional
        The underlying matching engine. If not provided, a new instance is created.
    seed : int, optional
        Random seed for the underlying matching engine (if created).
    """

    def __init__(
        self,
        *,
        traders: list[BaseTrader],
        news_feed: NewsFeed,
        matching_engine: MatchingEngine | None = None,
        seed: int | None = None,
    ) -> None:
        self._traders = traders
        self._news_feed = news_feed
        self._engine = matching_engine or MatchingEngine(seed=seed)
        self._view = MarketView(matching_engine=self._engine, news_feed=self._news_feed)

    @property
    def view(self) -> MarketView:
        """The read-only market view proxy."""
        return self._view

    def step(self, timestamp: datetime) -> list[Trade]:
        """Advance the simulation by one discrete tick.

        Queries all traders for new orders, submits them to the matching engine,
        triggers matching, and records executions.

        Parameters
        ----------
        timestamp : datetime
            The virtual timestamp of this simulation tick.

        Returns
        -------
        list[Trade]
            The list of trades executed during this tick.
        """
        for trader in self._traders:
            orders = trader.place(market_view=self._view, timestamp=timestamp)
            if orders is not None and not orders.is_empty:
                self._engine.place(orders=orders)

        trades = self._engine.match(timestamp=timestamp).trades
        self._view.update(trades=trades)
        return trades
