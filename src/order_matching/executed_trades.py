from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandera.typing.polars import LazyFrame

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

    def to_frame(self) -> LazyFrame[TradeDataSchema]:
        """Get polars DataFrame of all stored trades.

        .. deprecated:: 0.5.0
            Use ``PolarsExporter().export_trades(trades)`` instead.
            This method will be removed in version 1.0.0.

        Returns
        -------
        LazyFrame[TradeDataSchema]
            polars LazyFrame of all stored trades
        """
        from order_matching.exporters.polars import PolarsExporter

        return PolarsExporter().export_trades(self)

    def __add__(self, other: ExecutedTrades) -> ExecutedTrades:
        trades = ExecutedTrades()
        trades.add(trades=self.trades)
        trades.add(trades=other.trades)
        return trades
