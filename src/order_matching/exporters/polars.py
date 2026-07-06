from __future__ import annotations

from dataclasses import asdict
from typing import cast

import polars as pl
from pandera.typing.polars import LazyFrame

from order_matching.executed_trades import ExecutedTrades
from order_matching.exporters.base import Exporter
from order_matching.orders import Orders
from order_matching.schemas import OrderDataSchema, TradeDataSchema


class PolarsExporter(Exporter[LazyFrame]):
    """Export collections to polars LazyFrame format."""

    def export_orders(self, orders: Orders) -> LazyFrame[OrderDataSchema]:
        """Export Orders to validated polars LazyFrame.

        Parameters
        ----------
        orders : Orders
            Orders collection to export

        Returns
        -------
        LazyFrame[OrderDataSchema]
            Validated polars LazyFrame with order data
        """
        if len(orders) == 0:
            return cast(LazyFrame[OrderDataSchema], OrderDataSchema.empty().lazy())

        data = [asdict(order) for order in orders]
        for d in data:
            d[OrderDataSchema.side] = d[OrderDataSchema.side].name
            d[OrderDataSchema.execution] = d[OrderDataSchema.execution].name
            d[OrderDataSchema.status] = d[OrderDataSchema.status].name
        return cast(LazyFrame[OrderDataSchema], pl.LazyFrame(data))

    def export_trades(self, trades: ExecutedTrades) -> LazyFrame[TradeDataSchema]:
        """Export ExecutedTrades to validated polars LazyFrame.

        Parameters
        ----------
        trades : ExecutedTrades
            Trades collection to export

        Returns
        -------
        LazyFrame[TradeDataSchema]
            Validated polars LazyFrame with trade data
        """
        trade_list = trades.trades
        if len(trade_list) == 0:
            return cast(LazyFrame[TradeDataSchema], TradeDataSchema.empty().lazy())

        data = [asdict(trade) for trade in trade_list]
        for d in data:
            d[TradeDataSchema.side] = d[TradeDataSchema.side].name
            d[TradeDataSchema.execution] = d[TradeDataSchema.execution].name
        return cast(LazyFrame[TradeDataSchema], pl.LazyFrame(data))
