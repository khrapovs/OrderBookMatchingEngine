from dataclasses import asdict
from datetime import datetime

import pandas as pd
import pytest

from order_matching.execution import Execution
from order_matching.schemas import TradeDataSchema
from order_matching.side import Side
from order_matching.trade import Trade


class TestTrade:
    @pytest.mark.parametrize("side", [Side.BUY, Side.SELL])
    @pytest.mark.parametrize("price", [1.2, 2.4])
    @pytest.mark.parametrize("size", [10.0, 4.1])
    @pytest.mark.parametrize("timestamp", pd.date_range(start="2022", periods=3))
    @pytest.mark.parametrize("incoming_order_id", ["a", "abc"])
    @pytest.mark.parametrize("book_order_id", ["a", "abc"])
    @pytest.mark.parametrize("trade_id", ["t", "tr"])
    @pytest.mark.parametrize("execution", [Execution.LIMIT, Execution.MARKET])
    def test_trade_required_defaults(
        self,
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
        trades = pd.DataFrame(asdict(trade), index=pd.Index([0])).assign(
            **{
                TradeDataSchema.side: lambda df: df[TradeDataSchema.side].astype(str),
                TradeDataSchema.execution: lambda df: df[TradeDataSchema.execution].astype(str),
            }
        )
        TradeDataSchema.validate(trades, lazy=True)
