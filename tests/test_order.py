from datetime import datetime

import polars as pl
import pytest

from order_matching.enums import Execution, Side, Status
from order_matching.order import LimitOrder, MarketOrder, Order


class TestOrder:
    @pytest.mark.parametrize("side", [Side.BUY, Side.SELL])
    @pytest.mark.parametrize("price", [1.2, 2.4])
    @pytest.mark.parametrize("size", [10, 4.1])
    @pytest.mark.parametrize(
        "timestamp",
        pl.datetime_range(start=datetime(2022, 1, 1), end=datetime(2022, 1, 3), interval="1d", eager=True).to_list(),
    )
    @pytest.mark.parametrize(
        "expiration",
        [
            None,
            *pl.datetime_range(
                start=datetime(2023, 1, 1), end=datetime(2023, 1, 3), interval="1d", eager=True
            ).to_list(),
        ],
    )
    @pytest.mark.parametrize("order_id", ["a", "b"])
    @pytest.mark.parametrize("trader_id", ["x", "y"])
    @pytest.mark.parametrize("execution", [Execution.LIMIT, Execution.MARKET])
    @pytest.mark.parametrize("status", [Status.OPEN, Status.CANCEL])
    @pytest.mark.parametrize("price_number_of_digits", [1, 3])
    def test_order_required_defaults(
        self,
        *,
        side: Side,
        price: float,
        size: float,
        timestamp: datetime,
        expiration: datetime,
        order_id: str,
        trader_id: str,
        execution: Execution,
        status: Status,
        price_number_of_digits: int,
    ) -> None:
        order = Order(
            side=side,
            price=price,
            size=size,
            timestamp=timestamp,
            expiration=expiration,
            order_id=order_id,
            trader_id=trader_id,
            execution=execution,
            status=status,
            price_number_of_digits=price_number_of_digits,
        )
        assert order.side == side
        assert order.price == round(number=price, ndigits=price_number_of_digits)
        assert order.size == size
        assert order.timestamp == timestamp
        assert order.expiration == expiration
        assert order.order_id == order_id
        assert order.trader_id == trader_id
        assert order.execution == execution
        assert order.status == status
        assert order.price_number_of_digits == price_number_of_digits


class TestLimitOrder:
    @pytest.mark.parametrize("side", [Side.BUY, Side.SELL])
    @pytest.mark.parametrize("price", [1.2, 2.4])
    @pytest.mark.parametrize("size", [10, 4.1])
    @pytest.mark.parametrize(
        "timestamp",
        pl.datetime_range(start=datetime(2022, 1, 1), end=datetime(2022, 1, 3), interval="1d", eager=True).to_list(),
    )
    @pytest.mark.parametrize("order_id", ["a", "b"])
    @pytest.mark.parametrize("trader_id", ["x", "y"])
    @pytest.mark.parametrize("price_number_of_digits", [1, 3])
    def test_order_required_defaults(
        self,
        *,
        side: Side,
        price: float,
        size: float,
        timestamp: datetime,
        order_id: str,
        trader_id: str,
        price_number_of_digits: int,
    ) -> None:
        order = LimitOrder(
            side=side,
            price=price,
            size=size,
            timestamp=timestamp,
            order_id=order_id,
            trader_id=trader_id,
            price_number_of_digits=price_number_of_digits,
        )
        assert order.side == side
        assert order.price == round(number=price, ndigits=price_number_of_digits)
        assert order.size == size
        assert order.timestamp == timestamp
        assert order.order_id == order_id
        assert order.trader_id == trader_id
        assert order.execution == Execution.LIMIT
        assert order.status == Status.OPEN
        assert order.price_number_of_digits == price_number_of_digits


class TestMarketOrder:
    @pytest.mark.parametrize("side", [Side.BUY, Side.SELL])
    @pytest.mark.parametrize("size", [10, 4.1])
    @pytest.mark.parametrize(
        "timestamp",
        pl.datetime_range(start=datetime(2022, 1, 1), end=datetime(2022, 1, 3), interval="1d", eager=True).to_list(),
    )
    @pytest.mark.parametrize("order_id", ["a", "b"])
    @pytest.mark.parametrize("trader_id", ["x", "y"])
    def test_order_required_defaults(
        self, *, side: Side, size: float, timestamp: datetime, order_id: str, trader_id: str
    ) -> None:
        order = MarketOrder(side=side, size=size, timestamp=timestamp, order_id=order_id, trader_id=trader_id)
        assert order.side == side
        assert order.price == 0 if side == side.SELL else float("inf")
        assert order.size == size
        assert order.timestamp == timestamp
        assert order.order_id == order_id
        assert order.trader_id == trader_id
        assert order.execution == Execution.MARKET
        assert order.status == Status.OPEN
        assert order.price_number_of_digits == 1
