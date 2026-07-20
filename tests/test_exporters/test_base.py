import pytest

from order_matching.executed_trades import ExecutedTrades
from order_matching.exporters import Exporter
from order_matching.orders import Orders


class ConcreteExporter(Exporter[dict]):
    """Concrete implementation for testing."""

    def export_orders(self, orders: Orders) -> dict:  # noqa: ARG002
        return {"orders": []}

    def export_trades(self, trades: ExecutedTrades) -> dict:  # noqa: ARG002
        return {"trades": []}


class TestExporter:
    """Tests for abstract Exporter base class."""

    def test_exporter_is_abstract(self) -> None:
        """Test that Exporter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Exporter()

    def test_concrete_exporter_can_be_instantiated(self) -> None:
        """Test that a concrete Exporter subclass can be instantiated."""
        exporter = ConcreteExporter()
        assert isinstance(exporter, Exporter)

    def test_export_orders_abstract(self) -> None:
        """Test that export_orders is an abstract method."""
        assert hasattr(Exporter, "export_orders")
        assert getattr(Exporter.export_orders, "__isabstractmethod__", False)

    def test_export_trades_abstract(self) -> None:
        """Test that export_trades is an abstract method."""
        assert hasattr(Exporter, "export_trades")
        assert getattr(Exporter.export_trades, "__isabstractmethod__", False)

    def test_concrete_implementation_export_orders(self) -> None:
        """Test that concrete implementation can export orders."""
        exporter = ConcreteExporter()
        orders = Orders()
        result = exporter.export_orders(orders)
        assert isinstance(result, dict)
        assert "orders" in result

    def test_concrete_implementation_export_trades(self) -> None:
        """Test that concrete implementation can export trades."""
        exporter = ConcreteExporter()
        trades = ExecutedTrades()
        result = exporter.export_trades(trades)
        assert isinstance(result, dict)
        assert "trades" in result
