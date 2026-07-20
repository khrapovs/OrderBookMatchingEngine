from datetime import datetime

from order_matching.executed_trades import ExecutedTrades
from order_matching.order_book import OrderBook
from order_matching.simulation.news_feed import NewsEvent, NewsFeed


class MarketView:
    """Read-only proxy to poll market summary statistics and news events.

    Parameters
    ----------
    order_book : OrderBook
        The simulation's underlying order book.
    news_feed : NewsFeed
        The simulation's central news feed.
    """

    def __init__(self, *, order_book: OrderBook, news_feed: NewsFeed) -> None:
        self._order_book = order_book
        self._news_feed = news_feed
        self._executed_trades: ExecutedTrades = ExecutedTrades()

    @property
    def executed_trades(self) -> ExecutedTrades:
        """Historical list of executed trades in the simulation."""
        return self._executed_trades

    def update(self, *, trades: ExecutedTrades) -> None:
        """Update the market view with newly executed trades.

        Parameters
        ----------
        trades : ExecutedTrades
            The list of trades executed during the latest step.
        """
        self._executed_trades += trades

    @property
    def max_bid(self) -> float | None:
        """The highest bid price currently in the order book."""
        bids = self._order_book.bids
        return max(bids.keys()) if bids else None

    @property
    def min_offer(self) -> float | None:
        """The lowest offer price currently in the order book."""
        offers = self._order_book.offers
        return min(offers.keys()) if offers else None

    @property
    def mid_price(self) -> float | None:
        """The mid price of the bid-ask spread."""
        bid = self.max_bid
        offer = self.min_offer
        return (bid + offer) / 2.0 if bid is not None and offer is not None else None

    @property
    def spread(self) -> float | None:
        """The difference between the lowest offer and highest bid price."""
        bid = self.max_bid
        offer = self.min_offer
        return offer - bid if bid is not None and offer is not None else None

    @property
    def last_trade_price(self) -> float | None:
        """The price of the most recently executed trade."""
        return self._executed_trades.last_trade_price

    @property
    def bids_depth(self) -> list[tuple[float, float]]:
        """Bids price levels and total size at each level, sorted by price descending.

        Returns
        -------
        list[tuple[float, float]]
            List of (price, size) tuples.
        """
        bids = self._order_book.bids
        sorted_prices = sorted(bids.keys(), reverse=True)
        return [(price, sum(order.size for order in bids[price])) for price in sorted_prices]

    @property
    def asks_depth(self) -> list[tuple[float, float]]:
        """Asks price levels and total size at each level, sorted by price ascending.

        Returns
        -------
        list[tuple[float, float]]
            List of (price, size) tuples.
        """
        offers = self._order_book.offers
        sorted_prices = sorted(offers.keys())
        return [(price, sum(order.size for order in offers[price])) for price in sorted_prices]

    def get_news(self, timestamp: datetime) -> list[NewsEvent]:
        """Poll the news feed for all events up to the given timestamp.

        Parameters
        ----------
        timestamp : datetime
            The query timestamp.

        Returns
        -------
        list[NewsEvent]
            The list of matching news events.
        """
        return self._news_feed.get_news(timestamp=timestamp)

    def __setattr__(self, name: str, value: object) -> None:  # noqa: PLR0917
        if name in ("_order_book", "_news_feed", "_executed_trades"):
            super().__setattr__(name, value)
        else:
            raise AttributeError("MarketView is read-only")
