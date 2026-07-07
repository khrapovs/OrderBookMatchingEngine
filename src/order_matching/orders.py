from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Sequence

if TYPE_CHECKING:
    from pandera.typing.polars import LazyFrame

    from order_matching.schemas import OrderDataSchema

from order_matching.order import Order


class Orders:
    """Storage class for orders.

    Parameters
    ----------
    orders
    """

    def __init__(self, orders: Sequence[Order] | None = None) -> None:
        self.orders = list() if orders is None else list(orders)
        self._sort_orders_inplace()

    def add(self, orders: list[Order]) -> None:
        """Add new orders to the storage and sort them by timestamp.

        Parameters
        ----------
        orders
        """
        self.orders.extend(orders)
        self._sort_orders_inplace()

    def dequeue(self) -> Order:
        """Get the earliest order and remove it from the storage.

        Returns
        -------
        Order
            Earliest order
        """
        return self.orders.pop(0)

    def remove(self, orders: list[Order]) -> None:
        """Remove a list of orders from the storage matching by `order_id`.

        Partially executed orders may have their properties changed, hence matching is done only based on the id.

        Parameters
        ----------
        orders
        """
        for order_to_remove in orders:
            if order_to_remove.order_id in self._order_ids:
                self.orders.remove(self._get_order(order_id=order_to_remove.order_id))

    def to_frame(self) -> LazyFrame[OrderDataSchema]:
        """Get polars LazyFrame with all orders in the storage.

        .. deprecated:: 0.5.0
            Use ``PolarsExporter().export_orders(orders)`` instead.
            This method will be removed in version 1.0.0.

        Returns
        -------
        LazyFrame[OrderDataSchema]
        """
        from order_matching.exporters.polars import PolarsExporter

        return PolarsExporter().export_orders(self)

    @property
    def is_empty(self) -> bool:
        """Check if the storage is empty."""
        return len(self.orders) == 0

    def __add__(self, other: Orders) -> Orders:
        orders = Orders()
        orders.add(orders=self.orders)
        orders.add(orders=other.orders)
        return orders

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Orders):
            return NotImplemented
        else:
            return self.orders == other.orders

    def __iter__(self) -> Iterator[Order]:
        return iter(self.orders)

    def __next__(self) -> Order:
        return next(self.__iter__())

    def __len__(self) -> int:
        return len(self.orders)

    def _sort_orders_inplace(self) -> None:
        self.orders.sort(key=lambda order: order.timestamp)

    @property
    def _order_ids(self) -> list[str]:
        return [order.order_id for order in self.orders]

    def _get_order(self, order_id: str) -> Order:
        orders = [order for order in self.orders if order.order_id == order_id]
        assert len(orders) <= 1
        return orders[0]
