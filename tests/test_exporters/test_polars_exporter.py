from order_matching.exporters.polars import PolarsExporter
from order_matching.orders import Orders
from order_matching.schemas import OrderDataSchema, TradeDataSchema


class TestPolarsExporter:
    def test_export_empty_orders(self) -> None:
        """Test exporting empty Orders collection returns empty schema."""
        exporter = PolarsExporter()
        orders = Orders()
        result = exporter.export_orders(orders)
        assert result.collect().equals(OrderDataSchema.empty())

    def test_export_orders_with_data(self) -> None:
        """Test exporting Orders with data validates against schema."""
        from datetime import datetime

        from order_matching.order import LimitOrder
        from order_matching.side import Side

        exporter = PolarsExporter()
        timestamp = datetime(2023, 1, 1)
        order = LimitOrder(
            side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="test_order", trader_id="test_trader"
        )
        orders = Orders([order])
        result = exporter.export_orders(orders)
        OrderDataSchema.validate(result, lazy=True)

    def test_export_empty_trades(self) -> None:
        """Test exporting empty ExecutedTrades returns empty schema."""
        from order_matching.executed_trades import ExecutedTrades

        exporter = PolarsExporter()
        trades = ExecutedTrades()
        result = exporter.export_trades(trades)
        assert result.collect().equals(TradeDataSchema.empty())

    def test_export_trades_with_data(self) -> None:
        """Test exporting ExecutedTrades with data validates against schema."""
        from datetime import datetime

        from order_matching.executed_trades import ExecutedTrades
        from order_matching.execution import Execution
        from order_matching.side import Side
        from order_matching.trade import Trade

        exporter = PolarsExporter()
        timestamp = datetime(2023, 1, 2)
        trade = Trade(
            side=Side.SELL,
            price=1.2,
            size=1.6,
            incoming_order_id="b",
            book_order_id="a",
            execution=Execution.LIMIT,
            trade_id="test_trade",
            timestamp=timestamp,
        )
        trades = ExecutedTrades([trade])
        result = exporter.export_trades(trades)
        TradeDataSchema.validate(result, lazy=True)
