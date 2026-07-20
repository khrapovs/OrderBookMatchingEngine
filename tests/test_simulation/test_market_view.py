from datetime import datetime

import pytest

from order_matching.enums import Side
from order_matching.executed_trades import ExecutedTrades
from order_matching.matching_engine import MatchingEngine
from order_matching.order import LimitOrder
from order_matching.orders import Orders
from order_matching.simulation.market_view import MarketView
from order_matching.simulation.news_feed import NewsEvent, NewsFeed
from order_matching.trade import Trade


def test_market_view_empty_state() -> None:
    engine = MatchingEngine(seed=42)
    news_feed = NewsFeed()
    view = MarketView(order_book=engine.unprocessed_orders, news_feed=news_feed)

    assert view.max_bid == 0
    assert view.min_offer == float("inf")
    assert view.mid_price == 0.0
    assert view.spread == float("inf")
    assert view.last_trade_price is None
    assert view.bids_depth == []
    assert view.asks_depth == []
    assert view.get_news(datetime(2023, 1, 1)) == []

    with pytest.raises(AttributeError):
        setattr(view, "mid_price", 100.0)  # noqa


def test_market_view_with_orders_and_trades() -> None:
    engine = MatchingEngine(seed=42)
    news_feed = NewsFeed([NewsEvent(timestamp=datetime(2023, 1, 1, 10, 0), headline="News 1", impact=0.1)])

    t1 = datetime(2023, 1, 1, 10, 0)
    buy_1 = LimitOrder(side=Side.BUY, price=100.0, size=10.0, timestamp=t1, order_id="b1", trader_id="t_buy")
    buy_2 = LimitOrder(side=Side.BUY, price=99.0, size=5.0, timestamp=t1, order_id="b2", trader_id="t_buy")
    sell_1 = LimitOrder(side=Side.SELL, price=102.0, size=8.0, timestamp=t1, order_id="s1", trader_id="t_sell")

    engine.place(Orders([buy_1, buy_2, sell_1]))

    executed_trades = ExecutedTrades(
        trades=[
            Trade(
                side=Side.BUY,
                price=101.0,
                size=2.0,
                incoming_order_id="in_1",
                book_order_id="bk_1",
                timestamp=t1,
                execution=buy_1.execution,
                trade_id="trade_1",
            )
        ]
    )

    view = MarketView(order_book=engine.unprocessed_orders, news_feed=news_feed)
    view.update(trades=executed_trades)

    assert view.max_bid == 100.0
    assert view.min_offer == 102.0
    assert view.mid_price == 101.0
    assert view.spread == 2.0
    assert view.last_trade_price == 101.0
    assert view.bids_depth == [(100.0, 10.0), (99.0, 5.0)]
    assert view.asks_depth == [(102.0, 8.0)]
    assert len(view.get_news(datetime(2023, 1, 1, 11, 0))) == 1
