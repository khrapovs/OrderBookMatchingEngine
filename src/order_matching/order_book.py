from collections import defaultdict
from datetime import datetime
from typing import cast

import polars as pl
from pandera.typing.polars import LazyFrame

from order_matching.order import Order
from order_matching.orders import Orders
from order_matching.schemas import OrderBookSummarySchema
from order_matching.side import Side

OrderBookOrdersType = dict[float, Orders]


class OrderBook:
    """Order Book storage class."""

    def __init__(self) -> None:
        self.bids: OrderBookOrdersType = defaultdict(Orders)
        self.offers: OrderBookOrdersType = defaultdict(Orders)
        self.orders_by_expiration: dict[datetime, Orders] = defaultdict(Orders)

    def append(self, incoming_order: Order) -> None:
        """Add one order to the order book.

        Parameters
        ----------
        incoming_order
            New order
        """
        orders = self._get_same_side_orders(incoming_order=incoming_order)
        orders[incoming_order.price].add(orders=[incoming_order])
        self.orders_by_expiration[incoming_order.expiration].add(orders=[incoming_order])

    def find_order_by_id(self, order_id: str) -> Order | None:
        """Find an order by its ID across bids and offers.

        Parameters
        ----------
        order_id
            The order ID to search for

        Returns
        -------
        Order | None
            The matching order, or None if not found
        """
        for orders in self.bids.values():
            for order in orders:
                if order.order_id == order_id:
                    return order
        for orders in self.offers.values():
            for order in orders:
                if order.order_id == order_id:
                    return order
        return None

    def remove(self, incoming_order: Order) -> None:
        """Remove one order from the order book.

        Parameters
        ----------
        incoming_order
            Order to be removed
        """
        orders = self._get_same_side_orders(incoming_order=incoming_order)
        orders[incoming_order.price].remove(orders=[incoming_order])
        self.orders_by_expiration[incoming_order.expiration].remove(orders=[incoming_order])
        if len(orders[incoming_order.price]) == 0:
            orders.pop(incoming_order.price)
        if len(self.orders_by_expiration[incoming_order.expiration]) == 0:
            self.orders_by_expiration.pop(incoming_order.expiration)

    def summary(self) -> LazyFrame[OrderBookSummarySchema]:
        """Summary of the order book as a polars LazyFrame.

        Returns
        -------
        LazyFrame[OrderBookSummarySchema]
            Summary of the order book as a polars LazyFrame
        """
        bid_prices = self._get_bid_prices()
        offer_prices = self._get_offer_prices()
        empty_df = OrderBookSummarySchema.empty().lazy()

        if len(bid_prices) == 0 and len(offer_prices) == 0:
            return cast(LazyFrame[OrderBookSummarySchema], empty_df)

        dtypes = [
            pl.col(OrderBookSummarySchema.price).cast(pl.Float64),
            pl.col(OrderBookSummarySchema.size).cast(pl.Float64),
            pl.col(OrderBookSummarySchema.count).cast(pl.Int64),
        ]
        bids = (
            pl.LazyFrame(
                {
                    OrderBookSummarySchema.side: [Side.BUY.name] * len(bid_prices),
                    OrderBookSummarySchema.price: bid_prices,
                    OrderBookSummarySchema.size: self._get_bid_sizes(),
                    OrderBookSummarySchema.count: self._get_bid_counts(),
                }
            ).with_columns(dtypes)
            if len(bid_prices) > 0
            else empty_df
        )

        offers = (
            pl.LazyFrame(
                {
                    OrderBookSummarySchema.side: [Side.SELL.name] * len(offer_prices),
                    OrderBookSummarySchema.price: offer_prices,
                    OrderBookSummarySchema.size: self._get_offer_sizes(),
                    OrderBookSummarySchema.count: self._get_offer_counts(),
                }
            ).with_columns(dtypes)
            if len(offer_prices) > 0
            else empty_df
        )

        return cast(LazyFrame[OrderBookSummarySchema], pl.concat([bids, offers], how="vertical"))

    @property
    def current_price(self) -> float:
        """Current market price."""
        return (self.max_bid + self.min_offer) / 2

    def get_opposite_side_orders(self, incoming_order: Order) -> OrderBookOrdersType:
        """Get orders on the opposite side.

        If incoming order is sell, then bids are returned.
        If incoming order is buy, then offers are returned.

        Parameters
        ----------
        incoming_order

        Returns
        -------
        OrderBookOrdersType
        """
        match incoming_order.side:  # noqa E501
            case Side.SELL:
                return self.bids
            case Side.BUY:
                return self.offers

    def get_subset(self, expiration: datetime) -> Orders:
        """Get orders with given expiration time.

        Parameters
        ----------
        expiration

        Returns
        -------
        Orders
        """
        return self.orders_by_expiration[expiration]

    def matching_order_exists(self, incoming_order: Order) -> bool:
        """Check that matching order exists.

        Parameters
        ----------
        incoming_order

        Returns
        -------
        bool
        """
        match incoming_order.side:
            case Side.SELL:
                return incoming_order.price <= self.max_bid and len(self.bids) > 0
            case Side.BUY:
                return incoming_order.price >= self.min_offer and len(self.offers) > 0

    def get_matching_sorted_opposite_side_prices(self, incoming_order: Order) -> list[float]:
        """Get sorted prices of the matching orders on the opposite side.

        Parameters
        ----------
        incoming_order

        Returns
        -------
        list[float]
        """
        prices = self._get_sorted_opposite_side_prices(incoming_order=incoming_order)
        match incoming_order.side:
            case Side.SELL:
                return list(filter(lambda price: price >= incoming_order.price, prices))
            case Side.BUY:
                return list(filter(lambda price: price <= incoming_order.price, prices))

    def get_imbalance(self, price_range: float = 0.1) -> float:
        r"""Calculate order book imbalance.

        Order book imbalance indicator is defined as
        $$
        \rho(L)=\frac{V_L^b-V_L^a}{V_L^b+V_L^a}\in[-1,1],
        $$
        where
        $$
        V_L^b=\sum_i Q_i^b\cdot\mathbf{1}\left[P_i^b\geq P^M-L\right],
        $$
        and
        $$
        V_L^a=\sum_i Q_i^a\cdot\mathbf{1}\left[P_i^a\leq P^M+L\right],
        $$
        are the total bid/ask volumes within $L>0$ from the market price.
        It is said that the market is balanced when $\rho\approx0$.
        The market is imbalanced and there exists demand (supply) pressure when $\rho>0$ ($\rho<0$).
        As it is clear from the formula,
        the imbalance can be computed at any distance $L$ from the market price.
        The higher the distance, the deeper looks this indicator into the order book.

        Parameters
        ----------
        price_range
            Left/right from the current market price

        Returns
        -------
        float
            Market imbalance indicator
        """
        summary = self.summary()
        if self._is_empty(summary):
            return 0
        elif self._is_empty(summary.filter(pl.col(OrderBookSummarySchema.side) == Side.SELL.name)):
            return 1
        elif self._is_empty(summary.filter(pl.col(OrderBookSummarySchema.side) == Side.BUY.name)):
            return -1
        else:
            return self._get_non_trivial_imbalance(price_range=price_range)

    @staticmethod
    def _is_empty(df: pl.LazyFrame) -> bool:
        return df.select(pl.col(OrderBookSummarySchema.side).count()).collect().item() == 0

    def _get_non_trivial_imbalance(self, price_range: float) -> float:
        schema = OrderBookSummarySchema
        upper_bound = self.current_price + price_range
        lower_bound = self.current_price - price_range
        summary_subset = self.summary().filter(pl.col(schema.price).is_between(lower_bound, upper_bound))
        buy_volume = (
            summary_subset.filter(pl.col(schema.side) == Side.BUY.name)
            .select(pl.col(schema.size).sum())
            .collect()
            .item()
        )
        sell_volume = (
            summary_subset.filter(pl.col(schema.side) == Side.SELL.name)
            .select(pl.col(schema.size).sum())
            .collect()
            .item()
        )
        if buy_volume + sell_volume > 0:
            return (buy_volume - sell_volume) / (buy_volume + sell_volume)
        else:
            return 0.0

    def _get_same_side_orders(self, incoming_order: Order) -> OrderBookOrdersType:
        match incoming_order.side:
            case Side.SELL:
                return self.offers
            case Side.BUY:
                return self.bids

    def _get_sorted_opposite_side_prices(self, incoming_order: Order) -> list[float]:
        is_sell_side = incoming_order.side == Side.SELL
        return sorted(self.get_opposite_side_orders(incoming_order=incoming_order).keys(), reverse=is_sell_side)

    def _get_bid_prices(self) -> list[float]:
        return self._get_order_prices(orders=self.bids)

    def _get_offer_prices(self) -> list[float]:
        return self._get_order_prices(orders=self.offers)

    def _get_bid_sizes(self) -> list[float]:
        return self._get_order_sizes(orders=self.bids, prices=self._get_bid_prices())

    def _get_offer_sizes(self) -> list[float]:
        return self._get_order_sizes(orders=self.offers, prices=self._get_offer_prices())

    def _get_bid_counts(self) -> list[int]:
        return self._get_order_counts(orders=self.bids, prices=self._get_bid_prices())

    def _get_offer_counts(self) -> list[int]:
        return self._get_order_counts(orders=self.offers, prices=self._get_offer_prices())

    @staticmethod
    def _get_order_prices(orders: OrderBookOrdersType) -> list[float]:
        return sorted(orders.keys())

    @staticmethod
    def _get_order_sizes(orders: OrderBookOrdersType, prices: list[float]) -> list[float]:
        return [sum(order.size for order in orders[price]) for price in prices]

    @staticmethod
    def _get_order_counts(orders: OrderBookOrdersType, prices: list[float]) -> list[int]:
        return [len(orders[price]) for price in prices]

    @property
    def max_bid(self) -> float:
        """Maximum bid price."""
        if self.bids:
            return max(self.bids.keys())
        else:
            return 0.0

    @property
    def min_offer(self) -> float:
        """Minimum offer price."""
        if self.offers:
            return min(self.offers.keys())
        else:
            return float("inf")
