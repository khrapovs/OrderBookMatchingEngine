from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from typing import cast

import polars as pl
from pandera.typing.polars import DataFrame

from order_matching.schemas import TradeDataSchema
from order_matching.trade import Trade


class ExecutedTrades:
    """Executed Trades.

    Storage class for collections of trades.

    Parameters
    ----------
    trades
        Trades
    """

    def __init__(self, trades: list[Trade] | None = None) -> None:
        self._trades: dict[datetime, list[Trade]] = defaultdict(list)
        if trades:
            self.add(trades=trades)

    @property
    def trades(self) -> list[Trade]:
        """List of trades."""
        trades = list()
        for same_time_trades in self._trades.values():
            trades.extend(same_time_trades)
        return trades

    def add(self, trades: list[Trade]) -> None:
        """Add new trades to the object.

        Parameters
        ----------
        trades
            List of new trades to append to existing ones
        """
        for trade in trades:
            self._trades[trade.timestamp].append(trade)

    def get(self, timestamp: datetime) -> list[Trade]:
        """Get subset by timestamp.

        Returns
        -------
        list[Trade]
            List of trades with the same timestamp
        """
        return self._trades[timestamp]

    def to_frame(self) -> DataFrame[TradeDataSchema]:
        """Get polars DataFrame of all stored trades.

        Returns
        -------
        DataFrame[TradeDataSchema]
            polars DataFrame of all stored trades
        """
        trades = self.trades
        if len(trades) == 0:
            return TradeDataSchema.empty()
        else:
            data = [asdict(trade) for trade in trades]
            for d in data:
                d[TradeDataSchema.side] = d[TradeDataSchema.side].name
                d[TradeDataSchema.execution] = d[TradeDataSchema.execution].name
            return cast(DataFrame[TradeDataSchema], pl.DataFrame(data))

    def __add__(self, other: ExecutedTrades) -> ExecutedTrades:
        trades = ExecutedTrades()
        trades.add(trades=self.trades)
        trades.add(trades=other.trades)
        return trades
