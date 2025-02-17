from datetime import datetime
from time import sleep

from order_matching.executed_trades import ExecutedTrades
from order_matching.order import Order
from order_matching.order_book import OrderBook
from order_matching.orders import Orders
from order_matching.random import get_faker
from order_matching.status import Status
from order_matching.trade import Trade


class MatchingEngine:
    """Order Book Matching Engine.

    Parameters
    ----------
    seed
        Random seed

    Examples
    --------
    >>> from datetime import datetime, timedelta
    >>> from pprint import pp
    >>> from order_matching.matching_engine import MatchingEngine
    >>> from order_matching.order import LimitOrder
    >>> from order_matching.side import Side
    >>> matching_engine = MatchingEngine(seed=123)
    >>> timestamp = datetime(2023, 1, 1)
    >>> transaction_timestamp = timestamp + timedelta(days=1)
    >>> buy_order = LimitOrder(side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="a", trader_id="x")
    >>> sell_order = LimitOrder(side=Side.SELL, price=0.8, size=1.6, timestamp=timestamp, order_id="b", trader_id="y")
    >>> executed_trades = matching_engine.match(orders=Orders([buy_order, sell_order]), timestamp=transaction_timestamp)
    >>> pp(executed_trades.trades)
    [Trade(side=SELL,
           price=1.2,
           size=1.6,
           incoming_order_id='b',
           book_order_id='a',
           execution=LIMIT,
           trade_id='c4da537c-1651-4dae-8486-7db30d67b366',
           timestamp=datetime.datetime(2023, 1, 2, 0, 0))]
    """

    def __init__(self, seed: int | None = None) -> None:
        self._seed = seed
        self._faker = get_faker(seed=seed)
        self._queue = Orders()
        self.unprocessed_orders = OrderBook()
        self._timestamp: datetime

    def match(self, timestamp: datetime, orders: Orders | None = None) -> ExecutedTrades:
        """Match incoming orders in price-time priority.

        Parameters
        ----------
        timestamp
            Timestamp of order matching
        orders
            Incoming orders. Will be matched with existing ones on the order book in

        Returns
        -------
        ExecutedTrades
            Executed trades storage object
        """
        sleep(1)
        self._timestamp = timestamp
        self._queue += orders if orders else Orders()
        self._queue += self._get_expired_orders()
        trades = ExecutedTrades()
        while not self._queue.is_empty:
            trades += self._match(order=self._queue.dequeue())
        return trades

    def _get_expired_orders(self) -> Orders:
        orders: list[Order] = list()
        for timestamp in filter(lambda t: t <= self._timestamp, self.unprocessed_orders.orders_by_expiration.keys()):
            orders.extend(self.unprocessed_orders.orders_by_expiration[timestamp])
        for order in orders:
            order.status = Status.CANCEL
        return Orders(orders)

    def _match(self, order: Order) -> ExecutedTrades:
        if order.status == Status.CANCEL:
            self.unprocessed_orders.remove(incoming_order=order)
            return ExecutedTrades()
        elif self.unprocessed_orders.matching_order_exists(incoming_order=order):
            return self._execute_trades(incoming_order=order)
        else:
            self.unprocessed_orders.append(incoming_order=order)
            return ExecutedTrades()

    def _execute_trades(self, incoming_order: Order) -> ExecutedTrades:
        trades = ExecutedTrades()
        for price in self.unprocessed_orders.get_matching_sorted_opposite_side_prices(incoming_order=incoming_order):
            trades += self._execute_trades_for_one_price(incoming_order=incoming_order, price=price)
        if incoming_order.size > 0:
            self.unprocessed_orders.append(incoming_order=incoming_order)
        return trades

    def _execute_trades_for_one_price(self, incoming_order: Order, price: float) -> ExecutedTrades:
        opposite_side_orders = self.unprocessed_orders.get_opposite_side_orders(incoming_order=incoming_order)
        trades, zero_size_orders = list(), list()
        for book_order in opposite_side_orders[price]:
            if incoming_order.size > 0:
                trades.append(self._execute_trade(incoming_order=incoming_order, book_order=book_order))
            if book_order.size == 0:
                zero_size_orders.append(book_order)
        opposite_side_orders[price].remove(orders=zero_size_orders)
        if len(list(filter(lambda order: order.size > 0, opposite_side_orders[price]))) == 0:
            opposite_side_orders.pop(price)
        return ExecutedTrades(trades=trades)

    def _execute_trade(self, incoming_order: Order, book_order: Order) -> Trade:
        trade = Trade(
            side=incoming_order.side,
            price=book_order.price,
            size=min(incoming_order.size, book_order.size),
            incoming_order_id=incoming_order.order_id,
            book_order_id=book_order.order_id,
            timestamp=self._timestamp,
            execution=incoming_order.execution,
            trade_id=self._faker.uuid4(),
        )
        incoming_order.size = max(0.0, incoming_order.size - trade.size)
        book_order.size = max(0.0, book_order.size - trade.size)
        return trade
