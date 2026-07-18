from dataclasses import asdict
from datetime import datetime

import polars as pl
import pytest

from order_matching.enums import Execution, Side
from order_matching.schemas import TradeDataSchema
from order_matching.trade import Trade


class TestTrade:
    @pytest.mark.parametrize("side", [Side.BUY, Side.SELL])
    @pytest.mark.parametrize("price", [1.2, 2.4])
    @pytest.mark.parametrize("size", [10.0, 4.1])
    @pytest.mark.parametrize(
        "timestamp",
        pl.datetime_range(start=datetime(2022, 1, 1), end=datetime(2022, 1, 3), interval="1d", eager=True).to_list(),
    )
    @pytest.mark.parametrize("incoming_order_id", ["a", "abc"])
    @pytest.mark.parametrize("book_order_id", ["a", "abc"])
    @pytest.mark.parametrize("trade_id", ["t", "tr"])
    @pytest.mark.parametrize("execution", [Execution.LIMIT, Execution.MARKET])
    def test_trade_required_defaults(
        self,
        *,
        side: Side,
        price: float,
        size: float,
        timestamp: datetime,
        incoming_order_id: str,
        book_order_id: str,
        trade_id: str,
        execution: Execution,
    ) -> None:
        trade = Trade(
            side=side,
            price=price,
            size=size,
            timestamp=timestamp,
            incoming_order_id=incoming_order_id,
            book_order_id=book_order_id,
            execution=execution,
            trade_id=trade_id,
        )
        assert trade.side == side
        assert trade.price == price
        assert trade.size == size
        assert trade.timestamp == timestamp
        assert trade.incoming_order_id == incoming_order_id
        assert trade.book_order_id == book_order_id
        assert trade.execution == execution
        assert trade.trade_id == trade_id
        trade_dict = asdict(trade)
        trade_dict[TradeDataSchema.side] = trade_dict[TradeDataSchema.side].name
        trade_dict[TradeDataSchema.execution] = trade_dict[TradeDataSchema.execution].name
        trades = pl.LazyFrame([trade_dict])
        TradeDataSchema.validate(trades, lazy=True)
