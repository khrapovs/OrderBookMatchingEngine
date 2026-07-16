from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from order_matching.matching_engine import MatchingEngine
from order_matching.order import LimitOrder, MarketOrder
from order_matching.orders import Orders
from order_matching.random import get_faker
from order_matching.side import Side
from order_matching.status import Status
from order_matching.trade import Trade


class TestMatchingEngine:
    def test_place(self) -> None:
        matching_engine = MatchingEngine()
        timestamp = datetime.now()
        buy_order = LimitOrder(side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="buy1", trader_id="x")
        sell_order = LimitOrder(
            side=Side.SELL, price=1.0, size=2.3, timestamp=timestamp, order_id="sell1", trader_id="y"
        )

        # Place them. They cross, but they should not match yet.
        matching_engine.place(orders=Orders([buy_order, sell_order]))

        # Verify they are in the book
        assert matching_engine.unprocessed_orders.find_order_by_id("buy1") == buy_order
        assert matching_engine.unprocessed_orders.find_order_by_id("sell1") == sell_order

        # Verify duplicate order ID in same request raises ValueError
        with pytest.raises(ValueError, match="Duplicate order ID in request"):
            matching_engine.place(orders=Orders([buy_order, buy_order]))

        # Verify duplicate order ID in book raises ValueError
        dup_buy = LimitOrder(side=Side.BUY, price=1.5, size=1.0, timestamp=timestamp, order_id="buy1", trader_id="z")
        with pytest.raises(ValueError, match="Duplicate order ID: buy1"):
            matching_engine.place(orders=Orders([dup_buy]))

    def test_matching_with_no_orders(self) -> None:
        matching_engine = MatchingEngine()
        executed_trades = matching_engine.match(timestamp=datetime.now())

        assert matching_engine.unprocessed_orders.bids == dict()
        assert matching_engine.unprocessed_orders.offers == dict()
        assert executed_trades.trades == []

    def test_matching_with_complete_order(self) -> None:
        order_book = MatchingEngine()

        assert order_book.unprocessed_orders.bids == dict()
        assert order_book.unprocessed_orders.offers == dict()
        assert order_book.unprocessed_orders.current_price == float("inf")

        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order_first = LimitOrder(
            side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="xyz", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([buy_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {buy_order_first.price: Orders([buy_order_first])}
        assert order_book.unprocessed_orders.offers == dict()
        assert order_book.unprocessed_orders.current_price == float("inf")
        assert executed_trades.trades == []

        sell_order_first = LimitOrder(
            side=Side.SELL, price=3.4, size=5.6, timestamp=timestamp, order_id="abc", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([sell_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {buy_order_first.price: Orders([buy_order_first])}
        assert order_book.unprocessed_orders.offers == {sell_order_first.price: Orders([sell_order_first])}
        assert order_book.unprocessed_orders.current_price == 2.3
        assert executed_trades.trades == []

        buy_order_second = LimitOrder(
            side=Side.BUY, price=buy_order_first.price, size=6.7, timestamp=timestamp, order_id="qwe", trader_id="x"
        )
        sell_order_second = LimitOrder(
            side=Side.SELL, price=5.9, size=9.3, timestamp=timestamp, order_id="def", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([buy_order_second])))
        order_book.match(timestamp=transaction_timestamp)
        order_book.place(orders=deepcopy(Orders([sell_order_second])))
        order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {
            buy_order_first.price: Orders([buy_order_first, buy_order_second])
        }
        assert order_book.unprocessed_orders.offers == {
            sell_order_first.price: Orders([sell_order_first]),
            sell_order_second.price: Orders([sell_order_second]),
        }
        assert order_book.unprocessed_orders.current_price == 2.3
        assert executed_trades.trades == []

    def test_matching_with_matching_offer_same_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        size = 1
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        sell_order = LimitOrder(side=Side.SELL, price=3, size=size, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order])}
        assert executed_trades.trades == []

        buy_order = LimitOrder(side=Side.BUY, price=4, size=size, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == [
            Trade(
                side=buy_order.side,
                size=size,
                price=sell_order.price,
                incoming_order_id=buy_order.order_id,
                book_order_id=sell_order.order_id,
                timestamp=transaction_timestamp,
                execution=buy_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]
        assert order_book.unprocessed_orders.current_price == float("inf")

    def test_matching_with_matching_bid_same_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        size = 1
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order = LimitOrder(side=Side.BUY, price=4, size=size, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.offers == {}
        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order])}
        assert executed_trades.trades == []

        sell_order = LimitOrder(side=Side.SELL, price=3, size=size, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=size,
                price=buy_order.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]
        assert order_book.unprocessed_orders.current_price == float("inf")

    def test_matching_with_matching_offer_smaller_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        sell_order = LimitOrder(side=Side.SELL, price=3, size=2, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order])}
        assert executed_trades.trades == []

        buy_order = LimitOrder(side=Side.BUY, price=4, size=1, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        sell_order_modified = deepcopy(sell_order)
        sell_order_modified.size -= buy_order.size

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order_modified])}
        assert executed_trades.trades == [
            Trade(
                side=buy_order.side,
                size=buy_order.size,
                price=sell_order.price,
                incoming_order_id=buy_order.order_id,
                book_order_id=sell_order.order_id,
                timestamp=transaction_timestamp,
                execution=buy_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]
        assert order_book.unprocessed_orders.current_price == 1.5

    def test_matching_with_matching_bid_smaller_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order = LimitOrder(side=Side.BUY, price=4, size=2, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.offers == {}
        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order])}
        assert executed_trades.trades == []

        sell_order = LimitOrder(side=Side.SELL, price=3, size=1, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        buy_order_modified = deepcopy(buy_order)
        buy_order_modified.size -= sell_order.size

        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order_modified])}
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=sell_order.size,
                price=buy_order.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]
        assert order_book.unprocessed_orders.current_price == float("inf")

    def test_matching_with_matching_offer_bigger_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        sell_order = LimitOrder(side=Side.SELL, price=3, size=1, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order])}
        assert executed_trades.trades == []

        buy_order = LimitOrder(side=Side.BUY, price=4, size=2, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        buy_order_modified = deepcopy(buy_order)
        buy_order_modified.size -= sell_order.size

        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order_modified])}
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == [
            Trade(
                side=buy_order.side,
                size=buy_order_modified.size,
                price=sell_order.price,
                incoming_order_id=buy_order.order_id,
                book_order_id=sell_order.order_id,
                timestamp=transaction_timestamp,
                execution=buy_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]
        assert order_book.unprocessed_orders.current_price == float("inf")

    def test_matching_with_matching_offer_bigger_size_and_multiple_bids(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        matching_order = LimitOrder(side=Side.BUY, price=5, size=1, timestamp=timestamp, order_id="c", trader_id="x")
        buy_orders = [
            LimitOrder(side=Side.BUY, price=3, size=2, timestamp=timestamp, order_id="a", trader_id="x"),
            LimitOrder(side=Side.BUY, price=4, size=3, timestamp=timestamp, order_id="b", trader_id="x"),
            matching_order,
        ]
        sell_order = LimitOrder(side=Side.SELL, price=5, size=10, timestamp=timestamp, order_id="d", trader_id="x")
        sell_orders = [sell_order]
        order_book.place(orders=deepcopy(Orders(buy_orders)))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {
            buy_orders[0].price: Orders([buy_orders[0]]),
            buy_orders[1].price: Orders([buy_orders[1]]),
            matching_order.price: Orders([matching_order]),
        }
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == []

        order_book.place(orders=deepcopy(Orders(sell_orders)))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        sell_order_modified = deepcopy(sell_order)
        sell_order_modified.size -= matching_order.size

        assert order_book.unprocessed_orders.bids == {
            buy_orders[0].price: Orders([buy_orders[0]]),
            buy_orders[1].price: Orders([buy_orders[1]]),
        }
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order_modified])}
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=matching_order.size,
                price=sell_order.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=matching_order.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]

    def test_matching_with_matching_bid_bigger_size_and_multiple_offers(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        matching_order = LimitOrder(side=Side.SELL, price=6, size=1, timestamp=timestamp, order_id="c", trader_id="x")
        sell_orders = [
            LimitOrder(side=Side.SELL, price=7, size=2, timestamp=timestamp, order_id="a", trader_id="x"),
            LimitOrder(side=Side.SELL, price=8, size=3, timestamp=timestamp, order_id="b", trader_id="x"),
            matching_order,
        ]
        buy_order = LimitOrder(side=Side.BUY, price=6, size=10, timestamp=timestamp, order_id="d", trader_id="x")
        buy_orders = [buy_order]
        order_book.place(orders=deepcopy(Orders(sell_orders)))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.offers == {
            sell_orders[0].price: Orders([sell_orders[0]]),
            sell_orders[1].price: Orders([sell_orders[1]]),
            matching_order.price: Orders([matching_order]),
        }
        assert order_book.unprocessed_orders.bids == {}
        assert executed_trades.trades == []

        order_book.place(orders=deepcopy(Orders(buy_orders)))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        buy_order_modified = deepcopy(buy_order)
        buy_order_modified.size -= matching_order.size

        assert order_book.unprocessed_orders.offers == {
            sell_orders[0].price: Orders([sell_orders[0]]),
            sell_orders[1].price: Orders([sell_orders[1]]),
        }
        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order_modified])}
        assert executed_trades.trades == [
            Trade(
                side=buy_order.side,
                size=matching_order.size,
                price=buy_order.price,
                incoming_order_id=buy_order.order_id,
                book_order_id=matching_order.order_id,
                timestamp=transaction_timestamp,
                execution=buy_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]

    def test_matching_with_matching_bid_bigger_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order = LimitOrder(side=Side.BUY, price=4, size=1, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.offers == {}
        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order])}
        assert executed_trades.trades == []

        sell_order = LimitOrder(side=Side.SELL, price=3, size=2, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        sell_order_modified = deepcopy(sell_order)
        sell_order_modified.size -= buy_order.size

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order_modified])}
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=sell_order_modified.size,
                price=buy_order.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]
        assert order_book.unprocessed_orders.current_price == 1.5

    def test_matching_with_multiple_matching_offers_bigger_size(self) -> None:
        order_book = MatchingEngine(seed=42)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        sell_order_first = LimitOrder(
            side=Side.SELL, price=3, size=1, timestamp=timestamp, order_id="abc", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([sell_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order_first.price: Orders([sell_order_first])}
        assert executed_trades.trades == []

        sell_order_second = LimitOrder(
            side=Side.SELL, price=3, size=0.5, timestamp=timestamp, order_id="qwe", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([sell_order_second])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {
            sell_order_first.price: Orders([sell_order_first, sell_order_second])
        }
        assert executed_trades.trades == []

        buy_order = LimitOrder(side=Side.BUY, price=4, size=2, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        buy_order_modified = deepcopy(buy_order)
        buy_order_modified.size -= sell_order_first.size + sell_order_second.size

        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order_modified])}
        assert order_book.unprocessed_orders.offers == {}
        faker = get_faker(seed=42)
        assert executed_trades.trades == [
            Trade(
                side=buy_order.side,
                size=sell_order_first.size,
                price=sell_order_first.price,
                incoming_order_id=buy_order.order_id,
                book_order_id=sell_order_first.order_id,
                timestamp=transaction_timestamp,
                execution=buy_order.execution,
                trade_id=faker.uuid4(),
            ),
            Trade(
                side=buy_order.side,
                size=sell_order_second.size,
                price=sell_order_second.price,
                incoming_order_id=buy_order.order_id,
                book_order_id=sell_order_second.order_id,
                timestamp=transaction_timestamp,
                execution=buy_order.execution,
                trade_id=faker.uuid4(),
            ),
        ]
        assert order_book.unprocessed_orders.current_price == float("inf")

    def test_matching_with_multiple_matching_bids_bigger_size(self) -> None:
        order_book = MatchingEngine(seed=66)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order_first = LimitOrder(side=Side.BUY, price=4, size=1, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {buy_order_first.price: Orders([buy_order_first])}
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == []

        buy_order_second = LimitOrder(
            side=Side.BUY, price=4, size=0.5, timestamp=timestamp, order_id="qwe", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([buy_order_second])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {
            buy_order_first.price: Orders([buy_order_first, buy_order_second])
        }
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == []

        sell_order = LimitOrder(side=Side.SELL, price=3, size=2, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        sell_order_modified = deepcopy(sell_order)
        sell_order_modified.size -= buy_order_first.size + buy_order_second.size

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order.price: Orders([sell_order_modified])}
        assert len(executed_trades.trades) == 2
        faker = get_faker(seed=66)
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=buy_order_first.size,
                price=buy_order_first.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order_first.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=faker.uuid4(),
            ),
            Trade(
                side=sell_order.side,
                size=buy_order_second.size,
                price=buy_order_second.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order_second.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=faker.uuid4(),
            ),
        ]

        assert order_book.unprocessed_orders.current_price == 1.5

    def test_matching_does_not_leave_zero_size_orders_behind(self) -> None:
        order_book = MatchingEngine(seed=66)
        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order_first = LimitOrder(side=Side.BUY, price=4, size=1, timestamp=timestamp, order_id="a", trader_id="x")
        buy_order_second = LimitOrder(side=Side.BUY, price=4, size=1, timestamp=timestamp, order_id="b", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order_first, buy_order_second])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {
            buy_order_first.price: Orders([buy_order_first, buy_order_second])
        }
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == []

        sell_order = LimitOrder(side=Side.SELL, price=3.5, size=1.5, timestamp=timestamp, order_id="qwe", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        sell_order_modified = deepcopy(sell_order)
        sell_order_modified.size -= buy_order_first.size
        buy_order_second_modified = deepcopy(buy_order_second)
        buy_order_second_modified.size -= sell_order.size - buy_order_first.size

        assert order_book.unprocessed_orders.bids == {buy_order_second.price: Orders([buy_order_second_modified])}
        assert order_book.unprocessed_orders.offers == {}
        faker = get_faker(seed=66)
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=buy_order_first.size,
                price=buy_order_first.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order_first.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=faker.uuid4(),
            ),
            Trade(
                side=sell_order.side,
                size=buy_order_first.size + buy_order_second.size - sell_order.size,
                price=buy_order_second.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order_second.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=faker.uuid4(),
            ),
        ]

    def test_matching_time_preference(self) -> None:
        order_book = MatchingEngine(seed=42)

        timestamp = datetime(2022, 1, 5)
        time_delta = timedelta(days=1)
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order_first = LimitOrder(side=Side.BUY, price=4, size=1, timestamp=timestamp, order_id="abc", trader_id="x")
        buy_order_second = LimitOrder(
            side=Side.BUY, price=4, size=1, timestamp=timestamp - time_delta, order_id="qwe", trader_id="x"
        )
        sell_order = LimitOrder(
            side=Side.SELL, price=4, size=0.5, timestamp=timestamp + time_delta, order_id="xyz", trader_id="x"
        )
        order_book.place(orders=deepcopy(Orders([sell_order, buy_order_first, buy_order_second])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        buy_order_second_modified = deepcopy(buy_order_second)
        buy_order_second_modified.size -= sell_order.size

        assert buy_order_first.timestamp > buy_order_second.timestamp
        assert order_book.unprocessed_orders.bids == {
            buy_order_first.price: Orders([buy_order_second_modified, buy_order_first])
        }
        assert order_book.unprocessed_orders.offers == {}
        assert executed_trades.trades == [
            Trade(
                side=sell_order.side,
                size=sell_order.size,
                price=buy_order_second.price,
                incoming_order_id=sell_order.order_id,
                book_order_id=buy_order_second.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]

    def test_matching_with_market_orders_only(self) -> None:
        order_book = MatchingEngine(seed=42)

        assert order_book.unprocessed_orders.bids == dict()
        assert order_book.unprocessed_orders.offers == dict()
        assert order_book.unprocessed_orders.current_price == float("inf")

        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order_first = MarketOrder(side=Side.BUY, size=2.3, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {buy_order_first.price: Orders([buy_order_first])}
        assert order_book.unprocessed_orders.offers == dict()
        assert order_book.unprocessed_orders.current_price == float("inf")
        assert executed_trades.trades == []

        sell_order_first = MarketOrder(side=Side.SELL, size=5.6, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        modified_sell_order_first = deepcopy(sell_order_first)
        modified_sell_order_first.size -= buy_order_first.size

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order_first.price: Orders([modified_sell_order_first])}
        assert order_book.unprocessed_orders.current_price == 0.0
        assert executed_trades.trades == [
            Trade(
                side=sell_order_first.side,
                size=buy_order_first.size,
                price=buy_order_first.price,
                incoming_order_id=sell_order_first.order_id,
                book_order_id=buy_order_first.order_id,
                timestamp=transaction_timestamp,
                execution=sell_order_first.execution,
                trade_id=get_faker(seed=42).uuid4(),
            )
        ]

    def test_matching_with_sell_market_order_after_limit_orders(self) -> None:
        order_book = MatchingEngine(seed=42)

        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_orders = [
            LimitOrder(side=Side.BUY, price=5.6, size=2.3, timestamp=timestamp, order_id="xyz", trader_id="x"),
            LimitOrder(side=Side.BUY, price=6.5, size=3.2, timestamp=timestamp, order_id="qwe", trader_id="x"),
        ]
        order_book.place(orders=deepcopy(Orders(buy_orders)))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert executed_trades.trades == []

        sell_order_first = MarketOrder(side=Side.SELL, size=10.0, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([sell_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        modified_sell_order_first = deepcopy(sell_order_first)
        modified_sell_order_first.size -= buy_orders[0].size + buy_orders[1].size

        assert order_book.unprocessed_orders.bids == {}
        assert order_book.unprocessed_orders.offers == {sell_order_first.price: Orders([modified_sell_order_first])}
        assert order_book.unprocessed_orders.current_price == 0.0
        faker = get_faker(seed=42)
        assert executed_trades.trades == [
            Trade(
                side=sell_order_first.side,
                size=buy_orders[1].size,
                price=buy_orders[1].price,
                incoming_order_id=sell_order_first.order_id,
                book_order_id=buy_orders[1].order_id,
                timestamp=transaction_timestamp,
                execution=sell_order_first.execution,
                trade_id=faker.uuid4(),
            ),
            Trade(
                side=sell_order_first.side,
                size=buy_orders[0].size,
                price=buy_orders[0].price,
                incoming_order_id=sell_order_first.order_id,
                book_order_id=buy_orders[0].order_id,
                timestamp=transaction_timestamp,
                execution=sell_order_first.execution,
                trade_id=faker.uuid4(),
            ),
        ]

    def test_matching_with_buy_market_orders_after_limit_orders(self) -> None:
        order_book = MatchingEngine(seed=2)

        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        sell_orders = [
            LimitOrder(side=Side.SELL, price=5.6, size=2.3, timestamp=timestamp, order_id="xyz", trader_id="x"),
            LimitOrder(side=Side.SELL, price=6.5, size=3.2, timestamp=timestamp, order_id="qwe", trader_id="x"),
        ]
        order_book.place(orders=deepcopy(Orders(sell_orders)))
        executed_trades = order_book.match(timestamp=transaction_timestamp)

        assert executed_trades.trades == []

        buy_order_first = MarketOrder(side=Side.BUY, size=10.0, timestamp=timestamp, order_id="abc", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order_first])))
        executed_trades = order_book.match(timestamp=transaction_timestamp)
        modified_buy_order_first = deepcopy(buy_order_first)
        modified_buy_order_first.size -= sell_orders[0].size + sell_orders[1].size

        assert order_book.unprocessed_orders.bids == {buy_order_first.price: Orders([modified_buy_order_first])}
        assert order_book.unprocessed_orders.offers == {}
        assert order_book.unprocessed_orders.current_price == float("inf")
        faker = get_faker(seed=2)
        assert executed_trades.trades == [
            Trade(
                side=buy_order_first.side,
                size=sell_orders[0].size,
                price=sell_orders[0].price,
                incoming_order_id=buy_order_first.order_id,
                book_order_id=sell_orders[0].order_id,
                timestamp=transaction_timestamp,
                execution=buy_order_first.execution,
                trade_id=faker.uuid4(),
            ),
            Trade(
                side=buy_order_first.side,
                size=sell_orders[1].size,
                price=sell_orders[1].price,
                incoming_order_id=buy_order_first.order_id,
                book_order_id=sell_orders[1].order_id,
                timestamp=transaction_timestamp,
                execution=buy_order_first.execution,
                trade_id=faker.uuid4(),
            ),
        ]

    def test_matching_with_order_cancellation(self) -> None:
        order_book = MatchingEngine()

        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order = LimitOrder(side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="xyz", trader_id="x")
        order_book.place(orders=deepcopy(Orders([buy_order])))
        order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([buy_order])}

        cancel_buy_order = deepcopy(buy_order)
        cancel_buy_order.status = Status.CANCEL
        order_book.place(orders=deepcopy(Orders([cancel_buy_order])))
        order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}

    def test_matching_with_order_cancellation_after_trading(self) -> None:
        order_book = MatchingEngine()

        timestamp = datetime.now()
        transaction_timestamp = timestamp + timedelta(days=1)
        buy_order = LimitOrder(side=Side.BUY, price=1.2, size=3.0, timestamp=timestamp, order_id="xyz", trader_id="x")
        sell_order = MarketOrder(side=Side.SELL, size=2.0, timestamp=timestamp, order_id="abc", trader_id="y")
        order_book.place(orders=deepcopy(Orders([buy_order, sell_order])))
        order_book.match(timestamp=transaction_timestamp)
        modified_buy_order = deepcopy(buy_order)
        modified_buy_order.size -= sell_order.size

        assert order_book.unprocessed_orders.bids == {buy_order.price: Orders([modified_buy_order])}

        cancel_buy_order = deepcopy(buy_order)

        assert cancel_buy_order != modified_buy_order
        assert cancel_buy_order.order_id == modified_buy_order.order_id
        assert cancel_buy_order.size != modified_buy_order.size

        cancel_buy_order.status = Status.CANCEL
        order_book.place(orders=deepcopy(Orders([cancel_buy_order])))
        order_book.match(timestamp=transaction_timestamp)

        assert order_book.unprocessed_orders.bids == {}

    def test_cancellation_of_expired_orders(self) -> None:
        matching_engine = MatchingEngine()

        timestamp = datetime.now()
        time_delta = timedelta(days=1)
        expiration = timestamp + time_delta
        order = LimitOrder(
            side=Side.BUY,
            price=1.2,
            size=3.0,
            timestamp=timestamp,
            expiration=expiration,
            order_id="xyz",
            trader_id="x",
        )
        matching_engine.place(orders=Orders([order]))
        matching_engine.match(timestamp=timestamp)

        assert matching_engine.unprocessed_orders.bids == {order.price: Orders([order])}
        assert matching_engine.unprocessed_orders.offers == dict()

        matching_engine.match(timestamp=timestamp + time_delta / 2)

        assert matching_engine.unprocessed_orders.bids == {order.price: Orders([order])}
        assert matching_engine.unprocessed_orders.offers == dict()

        matching_engine.match(timestamp=expiration)

        assert matching_engine.unprocessed_orders.bids == dict()
        assert matching_engine.unprocessed_orders.offers == dict()

    def test_removal_of_filled_orders(self) -> None:
        matching_engine = MatchingEngine(seed=1)
        t0 = datetime(2023, 1, 1)
        buy = LimitOrder(side=Side.BUY, price=100.0, size=10, timestamp=t0, order_id="A", trader_id="x")
        sell = LimitOrder(
            side=Side.SELL, price=100.0, size=10, timestamp=t0 + timedelta(seconds=1), order_id="B", trader_id="y"
        )
        matching_engine.place(orders=Orders([buy]))
        matching_engine.match(timestamp=t0)
        matching_engine.place(orders=Orders([sell]))
        matching_engine.match(timestamp=t0 + timedelta(seconds=1))  # "A" is fully filled

        order_book = matching_engine.unprocessed_orders

        assert order_book.bids == {}
        assert order_book.offers == {}
        assert order_book.orders_by_expiration == {}

    def test_live_order_eviction(self) -> None:
        matching_engine = MatchingEngine(seed=1)
        timestamp = datetime(2023, 1, 1)
        expiration = timestamp + timedelta(hours=1)

        # 1) rest "X" @100 with a finite expiration, then fully fill it
        order = LimitOrder(
            side=Side.BUY, price=100.0, size=10, timestamp=timestamp, order_id="X", trader_id="x", expiration=expiration
        )
        matching_engine.place(orders=Orders(orders=[order]))
        matching_engine.match(timestamp=timestamp)
        order = LimitOrder(
            side=Side.SELL,
            price=100.0,
            size=10,
            timestamp=timestamp + timedelta(seconds=1),
            order_id="B",
            trader_id="y",
        )
        matching_engine.place(orders=Orders(orders=[order]))
        matching_engine.match(timestamp=timestamp + timedelta(seconds=1))

        # 2) a brand-new LIVE order re-uses id "X" at the same price (default far expiration)
        order = LimitOrder(
            side=Side.BUY, price=100.0, size=5, timestamp=timestamp + timedelta(seconds=2), order_id="X", trader_id="z"
        )
        matching_engine.place(orders=Orders(orders=[order]))
        matching_engine.match(timestamp=timestamp + timedelta(seconds=2))

        # 3) advance time past expiration with any order -> expiry sweep fires
        order = LimitOrder(
            side=Side.SELL, price=999.0, size=1, timestamp=timestamp + timedelta(hours=2), order_id="D", trader_id="w"
        )
        matching_engine.place(orders=Orders(orders=[order]))
        matching_engine.match(timestamp=timestamp + timedelta(hours=2))

        # the live re-used-id "X" was evicted; expected ['X']
        assert [o.order_id for v in matching_engine.unprocessed_orders.bids.values() for o in v] == ["X"]

    def test_matching_with_benchmark(self, random_orders: Orders, benchmark: BenchmarkFixture) -> None:
        def place_and_match(orders: Orders) -> None:
            engine = MatchingEngine()
            engine.place(orders=orders)
            engine.match(timestamp=orders.orders[-1].timestamp)

        benchmark(function_to_benchmark=place_and_match, orders=random_orders)
