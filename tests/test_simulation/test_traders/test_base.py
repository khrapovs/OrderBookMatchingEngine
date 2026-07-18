from datetime import datetime

import pytest

from order_matching.matching_engine import MatchingEngine
from order_matching.orders import Orders
from order_matching.simulation.market_view import MarketView
from order_matching.simulation.news_feed import NewsFeed
from order_matching.simulation.traders.base import BaseTrader


class CustomMockTrader(BaseTrader):
    def place(self, *, market_view: MarketView, timestamp: datetime) -> Orders | None:  # noqa: ARG002
        return None


def test_base_trader_id() -> None:
    trader = CustomMockTrader(trader_id="trader_123")
    assert trader.trader_id == "trader_123"


def test_base_trader_place_raises_not_implemented() -> None:
    trader = BaseTrader(trader_id="base_1")
    engine = MatchingEngine()
    news = NewsFeed()
    view = MarketView(matching_engine=engine, news_feed=news)

    with pytest.raises(NotImplementedError):
        trader.place(market_view=view, timestamp=datetime(2023, 1, 1))
