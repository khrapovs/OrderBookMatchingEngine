from datetime import datetime, timedelta

from order_matching.order import LimitOrder
from order_matching.order_book import OrderBook
from order_matching.orders import Orders
from order_matching.schemas import OrderBookSummarySchema
from order_matching.side import Side


class TestOrderBook:
    timestamp = datetime.now()

    def test_init(self) -> None:
        order_book = OrderBook()

        assert order_book.bids == {}
        assert order_book.offers == {}
        assert order_book.current_price == float("inf")

    def test_append_with_same_price(self) -> None:
        order_book = OrderBook()

        buy_price, sell_price = 1.2, 1.3
        buy_orders = [
            LimitOrder(
                side=Side.BUY, price=buy_price, size=size, timestamp=self.timestamp, order_id=order_id, trader_id="x"
            )
            for size, order_id in zip([12, 65, 98], ["a", "b", "c"], strict=True)
        ]
        sell_orders = [
            LimitOrder(
                side=Side.SELL, price=sell_price, size=size, timestamp=self.timestamp, order_id=order_id, trader_id="y"
            )
            for size, order_id in zip([12, 65, 98], ["a", "b", "c"], strict=True)
        ]
        for order in [*buy_orders, *sell_orders]:
            order_book.append(incoming_order=order)

        assert order_book.bids == {buy_price: Orders(buy_orders)}
        assert order_book.offers == {sell_price: Orders(sell_orders)}
        assert order_book.current_price == (buy_price + sell_price) / 2

    def test_append(self) -> None:
        order_book = OrderBook()

        buy_order_first = LimitOrder(
            side=Side.BUY, price=1.2, size=2.3, timestamp=self.timestamp, order_id="xyz", trader_id="x"
        )
        order_book.append(incoming_order=buy_order_first)

        assert order_book.bids == {buy_order_first.price: Orders([buy_order_first])}
        assert order_book.offers == dict()
        assert order_book.current_price == float("inf")

        sell_order_first = LimitOrder(
            side=Side.SELL, price=3.4, size=5.6, timestamp=self.timestamp, order_id="abc", trader_id="x"
        )
        order_book.append(incoming_order=sell_order_first)

        assert order_book.bids == {buy_order_first.price: Orders([buy_order_first])}
        assert order_book.offers == {sell_order_first.price: Orders([sell_order_first])}
        assert order_book.current_price == 2.3

        buy_order_second = LimitOrder(
            side=Side.BUY,
            price=buy_order_first.price,
            size=6.7,
            timestamp=self.timestamp,
            order_id="qwe",
            trader_id="x",
        )
        sell_order_second = LimitOrder(
            side=Side.SELL, price=5.9, size=9.3, timestamp=self.timestamp, order_id="abc", trader_id="x"
        )
        order_book.append(incoming_order=buy_order_second)
        order_book.append(incoming_order=sell_order_second)

        assert order_book.bids == {buy_order_first.price: Orders([buy_order_first, buy_order_second])}
        assert order_book.offers == {
            sell_order_first.price: Orders([sell_order_first]),
            sell_order_second.price: Orders([sell_order_second]),
        }
        assert order_book.current_price == 2.3

    def test_append_remove_and_get_subset(self) -> None:
        order_book = OrderBook()

        assert order_book.get_subset(expiration=self.timestamp) == Orders()

        first_buy_order = self._get_sample_orders().orders[0]
        second_buy_order = self._get_sample_orders().orders[2]
        third_buy_order = self._get_sample_orders().orders[4]
        time_delta = timedelta(days=1)
        third_buy_order.expiration = self.timestamp + time_delta

        assert first_buy_order.price == second_buy_order.price
        assert first_buy_order.price != third_buy_order.price
        assert first_buy_order.side == second_buy_order.side
        assert first_buy_order.side == third_buy_order.side
        assert first_buy_order.expiration == second_buy_order.expiration
        assert first_buy_order.expiration != third_buy_order.expiration
        assert order_book.bids == dict()

        order_book.remove(incoming_order=first_buy_order)

        assert order_book.bids == dict()
        assert order_book.get_subset(expiration=self.timestamp) == Orders()

        order_book.append(incoming_order=first_buy_order)
        order_book.append(incoming_order=second_buy_order)
        order_book.append(incoming_order=third_buy_order)

        assert order_book.bids == {
            first_buy_order.price: Orders([first_buy_order, second_buy_order]),
            third_buy_order.price: Orders([third_buy_order]),
        }
        assert order_book.get_subset(expiration=self.timestamp) == Orders([first_buy_order, second_buy_order])
        assert order_book.get_subset(expiration=self.timestamp + time_delta) == Orders([third_buy_order])

        order_book.remove(incoming_order=first_buy_order)

        assert order_book.bids == {
            first_buy_order.price: Orders([second_buy_order]),
            third_buy_order.price: Orders([third_buy_order]),
        }
        assert order_book.get_subset(expiration=self.timestamp) == Orders([second_buy_order])
        assert order_book.get_subset(expiration=self.timestamp + time_delta) == Orders([third_buy_order])

        order_book.remove(incoming_order=second_buy_order)

        assert order_book.bids == {third_buy_order.price: Orders([third_buy_order])}
        assert order_book.get_subset(expiration=self.timestamp) == Orders()
        assert order_book.get_subset(expiration=self.timestamp + time_delta) == Orders([third_buy_order])

        order_book.remove(incoming_order=third_buy_order)

        assert order_book.bids == dict()
        assert order_book.get_subset(expiration=self.timestamp) == Orders()

    def test_order_book_summary(self) -> None:
        order_book = OrderBook()
        for order in self._get_sample_orders():
            order_book.append(incoming_order=order)
        summary = order_book.summary()

        OrderBookSummarySchema.validate(summary, lazy=True)
        assert summary.index.is_monotonic_increasing
        assert summary[OrderBookSummarySchema.price].is_monotonic_increasing
        assert order_book.current_price == 2.3

    def test_order_book_imbalance_one_buy_order(self) -> None:
        order_book = OrderBook()
        buy_orders = [
            LimitOrder(side=Side.BUY, price=1.3, size=38, timestamp=self.timestamp, order_id="x", trader_id="x")
        ]
        for order in [*buy_orders]:
            order_book.append(incoming_order=order)

        assert order_book.get_imbalance(price_range=0.1) == 1

    def test_order_book_imbalance_one_sell_order(self) -> None:
        order_book = OrderBook()
        sell_orders = [
            LimitOrder(side=Side.SELL, price=1.3, size=38, timestamp=self.timestamp, order_id="x", trader_id="x")
        ]
        for order in [*sell_orders]:
            order_book.append(incoming_order=order)

        assert order_book.get_imbalance(price_range=0.1) == -1

    def test_order_book_imbalance_with_equal_orders(self) -> None:
        order_book = OrderBook()
        buy_orders = [
            LimitOrder(side=Side.BUY, price=1.4, size=10, timestamp=self.timestamp, order_id="x", trader_id="x")
        ]
        sell_orders = [
            LimitOrder(side=Side.SELL, price=1.6, size=10, timestamp=self.timestamp, order_id="x", trader_id="y"),
            LimitOrder(side=Side.SELL, price=1.8, size=20, timestamp=self.timestamp, order_id="x", trader_id="y"),
        ]
        for order in [*buy_orders, *sell_orders]:
            order_book.append(incoming_order=order)

        assert order_book.get_imbalance(price_range=0.05) == 0
        assert order_book.get_imbalance(price_range=0.1) == 0
        assert order_book.get_imbalance(price_range=0.2) == 0
        assert order_book.get_imbalance(price_range=0.3) == (10 - 20 - 10) / (10 + 20 + 10)

    def test_order_book_imbalance_with_several_orders(self) -> None:
        order_book = OrderBook()
        buy_orders = [
            LimitOrder(side=Side.BUY, price=price, size=size, timestamp=self.timestamp, order_id="x", trader_id="x")
            for size, price in zip([12, 65, 98], [1.1, 1.3, 1.4], strict=True)
        ]
        sell_orders = [
            LimitOrder(side=Side.SELL, price=price, size=size, timestamp=self.timestamp, order_id="x", trader_id="y")
            for size, price in zip([8, 86, 72], [1.5, 1.7, 1.8], strict=True)
        ]
        for order in [*buy_orders, *sell_orders]:
            order_book.append(incoming_order=order)

        assert order_book.get_imbalance(price_range=0.1) == (98 - 8) / (98 + 8)
        assert order_book.get_imbalance(price_range=0.2) == (65 + 98 - 8) / (65 + 98 + 8)
        assert order_book.get_imbalance(price_range=0.3) == (65 + 98 - 8 - 86) / (65 + 98 + 8 + 86)
        assert order_book.get_imbalance(price_range=0.4) == (12 + 65 + 98 - 8 - 86 - 72) / (12 + 65 + 98 + 8 + 86 + 72)

    def _get_sample_orders(self) -> Orders:
        orders = [
            LimitOrder(side=Side.BUY, price=1.2, size=2.3, timestamp=self.timestamp, order_id="xyz", trader_id="x"),
            LimitOrder(side=Side.SELL, price=3.4, size=5.6, timestamp=self.timestamp, order_id="abc", trader_id="x"),
            LimitOrder(side=Side.BUY, price=1.2, size=6.7, timestamp=self.timestamp, order_id="qwe", trader_id="x"),
            LimitOrder(side=Side.SELL, price=5.9, size=9.3, timestamp=self.timestamp, order_id="abc", trader_id="x"),
            LimitOrder(side=Side.BUY, price=1.1, size=6.7, timestamp=self.timestamp, order_id="qwe", trader_id="x"),
        ]
        for order in orders:
            order.expiration = self.timestamp
        return Orders(orders)
