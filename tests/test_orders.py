from copy import deepcopy
from datetime import datetime, timedelta

import pytest

from order_matching.order import LimitOrder, Order
from order_matching.orders import Orders
from order_matching.schemas import OrderDataSchema
from order_matching.side import Side


class TestOrders:
    def test_init(self) -> None:
        order_queue = Orders()

        assert order_queue.orders == list()
        assert order_queue.is_empty

        orders = self._get_test_orders()
        order_queue = Orders(orders=orders)

        assert order_queue.orders != orders

        orders.sort(key=lambda order: order.timestamp)

        assert order_queue.orders == orders

    def test_dequeue(self) -> None:
        order_queue = Orders()
        orders = self._get_test_orders()
        order_queue.add(orders=orders)

        assert not order_queue.is_empty
        assert order_queue.orders == [orders[1], orders[0], orders[2], orders[3]]

        assert order_queue.dequeue() == orders[1]
        assert order_queue.dequeue() == orders[0]
        assert order_queue.dequeue() == orders[2]
        assert order_queue.dequeue() == orders[3]
        assert order_queue.is_empty

    @pytest.mark.parametrize("ids_to_remove", [[0], [2], [1, -1]])
    def test_remove(self, ids_to_remove: list[int]) -> None:
        orders = self._get_test_orders()
        orders_to_remove = deepcopy([orders[i] for i in ids_to_remove])
        order_queue = Orders()
        order_queue.remove(orders=orders_to_remove)

        assert order_queue == Orders()

        order_queue = Orders(orders=orders)
        for order in orders_to_remove:
            order.size /= 2
        order_queue.remove(orders=orders_to_remove)
        order_ids_to_remove = [order.order_id for order in orders_to_remove]
        expected_leftover_orders = [order for order in orders if order.order_id not in order_ids_to_remove]
        expected_queue = Orders(orders=expected_leftover_orders)

        assert order_queue == expected_queue

    def test_to_frame(self) -> None:
        order_queue = Orders()
        orders = self._get_test_orders()
        order_queue.add(orders=orders)

        OrderDataSchema.validate(order_queue.to_frame(), lazy=True)

    def test_dunder_add_and_len(self) -> None:
        order_queue_first = Orders()

        assert len(order_queue_first) == 0

        first_order, second_order = self._get_test_orders()[:2]
        order_queue_first.add(orders=[first_order])
        order_queue_second = Orders()
        order_queue_second.add(orders=[second_order])
        order_queue_third = Orders()
        order_queue_third.add(orders=[first_order])
        order_queue_all = Orders()
        order_queue_all.add(orders=[first_order, second_order, second_order])

        assert len(order_queue_first) == 1
        assert len(order_queue_second) == 1
        assert len(order_queue_third) == 1
        assert len(order_queue_all) == 3
        assert (order_queue_first + order_queue_second + order_queue_third).orders == [
            second_order,
            first_order,
            first_order,
        ]
        assert order_queue_first.orders == [first_order]
        assert order_queue_second.orders == [second_order]
        assert order_queue_third.orders == [first_order]

    @staticmethod
    def _get_test_orders() -> list[Order]:
        timestamp = datetime.now()
        return [
            LimitOrder(side=Side.SELL, price=4.0, size=10.0, timestamp=timestamp, order_id="a", trader_id="x"),
            LimitOrder(
                side=Side.BUY,
                price=4.0,
                size=12.0,
                timestamp=timestamp - timedelta(days=1),
                order_id="b",
                trader_id="x",
            ),
            LimitOrder(side=Side.BUY, price=4.0, size=7.0, timestamp=timestamp, order_id="c", trader_id="x"),
            LimitOrder(side=Side.SELL, price=3.0, size=8.0, timestamp=timestamp, order_id="d", trader_id="x"),
        ]
