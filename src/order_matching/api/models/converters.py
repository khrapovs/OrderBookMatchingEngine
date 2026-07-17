from datetime import datetime

from order_matching.api.models.requests import OrderRequest
from order_matching.api.models.responses import ExecutionStr, OrderResponse, SideStr, StatusStr, TradeResponse
from order_matching.executed_trades import ExecutedTrades
from order_matching.execution import Execution
from order_matching.order import LimitOrder, MarketOrder, Order
from order_matching.orders import Orders
from order_matching.side import Side
from order_matching.status import Status
from order_matching.trade import Trade


def side_from_str(s: str) -> Side:
    try:
        return Side[s]
    except KeyError:
        raise ValueError(f"Invalid side: {s}") from None


def side_to_str(side: Side) -> str:
    return side.name


def execution_from_str(s: str) -> Execution:
    try:
        return Execution[s]
    except KeyError:
        raise ValueError(f"Invalid execution: {s}") from None


def execution_to_str(exec: Execution) -> str:
    return exec.name


def status_from_str(s: str) -> Status:
    try:
        return Status[s]
    except KeyError:
        raise ValueError(f"Invalid status: {s}") from None


def status_to_str(stat: Status) -> str:
    return stat.name


def to_naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def request_to_domain_order(request: OrderRequest) -> Order:
    side = side_from_str(request.side.value)
    expiration = request.expiration if request.expiration is not None else datetime.max

    timestamp = to_naive(request.timestamp)
    expiration = to_naive(expiration)

    if request.order_type == "limit":
        return LimitOrder(
            side=side,
            price=request.price,
            size=request.size,
            timestamp=timestamp,
            order_id=request.order_id,
            trader_id=request.trader_id,
            expiration=expiration,
        )
    elif request.order_type == "market":
        return MarketOrder(
            side=side,
            size=request.size,
            timestamp=timestamp,
            order_id=request.order_id,
            trader_id=request.trader_id,
            expiration=expiration,
        )
    else:
        raise ValueError(f"Unknown order type: {request.order_type}")


def domain_order_to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        side=SideStr(side_to_str(order.side)),
        price=order.price,
        size=order.size,
        timestamp=order.timestamp,
        order_id=order.order_id,
        trader_id=order.trader_id,
        execution=ExecutionStr(execution_to_str(order.execution)),
        status=StatusStr(status_to_str(order.status)),
        expiration=order.expiration,
    )


def domain_trade_to_response(trade: Trade) -> TradeResponse:
    return TradeResponse(
        side=SideStr(side_to_str(trade.side)),
        price=trade.price,
        size=trade.size,
        incoming_order_id=trade.incoming_order_id,
        book_order_id=trade.book_order_id,
        execution=ExecutionStr(execution_to_str(trade.execution)),
        trade_id=trade.trade_id,
        timestamp=trade.timestamp,
    )


def domain_orders_to_response(orders: Orders) -> list[OrderResponse]:
    return [domain_order_to_response(order) for order in orders.orders]


def domain_trades_to_response(executed_trades: ExecutedTrades) -> list[TradeResponse]:
    return [domain_trade_to_response(trade) for trade in executed_trades.trades]
