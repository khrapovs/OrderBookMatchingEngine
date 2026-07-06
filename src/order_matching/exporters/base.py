from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from order_matching.executed_trades import ExecutedTrades
    from order_matching.orders import Orders

T = TypeVar("T")


class Exporter(ABC, Generic[T]):
    """Abstract base class for data exporters.

    Type parameter T represents the output format type
    (e.g., LazyFrame, dict, str for JSON/CSV).
    """

    @abstractmethod
    def export_orders(self, orders: Orders) -> T:
        """Convert Orders collection to target format.

        Parameters
        ----------
        orders : Orders
            Orders collection to export

        Returns
        -------
        T
            Exported data in target format
        """
        pass

    @abstractmethod
    def export_trades(self, trades: ExecutedTrades) -> T:
        """Convert ExecutedTrades collection to target format.

        Parameters
        ----------
        trades : ExecutedTrades
            Trades collection to export

        Returns
        -------
        T
            Exported data in target format
        """
        pass
