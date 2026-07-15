from dataclasses import replace
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import (
    domain_order_to_response,
    domain_trade_to_response,
    request_to_domain_order,
)
from order_matching.api.models.requests import MatchRequest, PlaceOrdersRequest, ResetRequest
from order_matching.api.models.responses import (
    MatchResponse,
    OrderBookResponse,
    PlaceOrdersResponse,
    ResetResponse,
    SideStr,
    SummaryLevel,
    TradeHistoryResponse,
)
from order_matching.matching_engine import MatchingEngine
from order_matching.orders import Orders
from order_matching.status import Status

router = APIRouter()


def _order_id_exists(*, engine: MatchingEngine, order_id: str) -> bool:
    """Check if an order_id exists in the engine's active orders."""
    for _price, orders in engine.unprocessed_orders.bids.items():
        for order in orders.orders:
            if order.order_id == order_id:
                return True
    for _price, orders in engine.unprocessed_orders.offers.items():
        for order in orders.orders:
            if order.order_id == order_id:
                return True
    return False


@router.post("/orders")
def place_orders(request: Request, payload: PlaceOrdersRequest, engine: MatchingEngineDep) -> PlaceOrdersResponse:
    if not payload.orders:
        raise HTTPException(status_code=422, detail="At least one order must be provided")

    # 15.2 Check for duplicate IDs in the request itself
    request_ids = [order.order_id for order in payload.orders]
    if len(request_ids) != len(set(request_ids)):
        raise HTTPException(status_code=400, detail="Duplicate order ID in request")

    # Check if any ID already exists in the engine's active orders
    for order in payload.orders:
        if _order_id_exists(engine=engine, order_id=order.order_id):
            raise HTTPException(status_code=400, detail=f"Duplicate order ID: {order.order_id}")

    # Convert request orders to domain Orders
    domain_orders_list = [request_to_domain_order(o) for o in payload.orders]
    domain_orders = Orders(domain_orders_list)

    # Call matching_engine.match() with orders and first order's timestamp
    first_order_timestamp = payload.orders[0].timestamp
    executed_trades = engine.match(orders=domain_orders, timestamp=first_order_timestamp)

    # Accumulate executed trades in app state
    request.app.state.trades.extend(executed_trades.trades)

    return PlaceOrdersResponse(
        message=f"Successfully placed {len(payload.orders)} orders",
        orders=[domain_order_to_response(o) for o in domain_orders.orders],
    )


@router.post("/match")
def match_orders(request: Request, payload: MatchRequest, engine: MatchingEngineDep) -> MatchResponse:
    executed_trades = engine.match(timestamp=payload.timestamp)

    # Accumulate trades in app state
    request.app.state.trades.extend(executed_trades.trades)

    trades_res = [domain_trade_to_response(t) for t in executed_trades.trades]
    return MatchResponse(trades=trades_res)


@router.get("/orders")
def get_order_book(engine: MatchingEngineDep) -> OrderBookResponse:
    bids = {}
    for price, orders in engine.unprocessed_orders.bids.items():
        bids[price] = [domain_order_to_response(o) for o in orders.orders]

    offers = {}
    for price, orders in engine.unprocessed_orders.offers.items():
        offers[price] = [domain_order_to_response(o) for o in orders.orders]

    return OrderBookResponse(bids=bids, offers=offers)


@router.get("/trades")
def get_trades(
    request: Request, _engine: MatchingEngineDep, from_timestamp: datetime | None = None
) -> TradeHistoryResponse:
    trades = request.app.state.trades
    if from_timestamp is not None:
        trades = [t for t in trades if t.timestamp >= from_timestamp]

    trades_res = [domain_trade_to_response(t) for t in trades]
    return TradeHistoryResponse(trades=trades_res)


@router.delete("/orders/{order_id}")
def cancel_order(order_id: str, engine: MatchingEngineDep) -> dict[str, str]:
    order_to_cancel = None
    # Look up in bids
    for _price, orders in engine.unprocessed_orders.bids.items():
        for order in orders.orders:
            if order.order_id == order_id:
                order_to_cancel = order
                break
        if order_to_cancel:
            break

    # Look up in offers if not found in bids
    if not order_to_cancel:
        for _price, orders in engine.unprocessed_orders.offers.items():
            for order in orders.orders:
                if order.order_id == order_id:
                    order_to_cancel = order
                    break
            if order_to_cancel:
                break

    if not order_to_cancel:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    # Create cancel order and trigger match
    cancel_order = replace(order_to_cancel, status=Status.CANCEL)
    engine.match(orders=Orders([cancel_order]), timestamp=order_to_cancel.timestamp)

    return {"message": f"Order {order_id} cancelled successfully"}


@router.post("/reset")
def reset_engine(request: Request, payload: ResetRequest) -> ResetResponse:
    # Reinitialize engine in app state
    new_engine = MatchingEngine(seed=payload.seed)
    request.app.state.engine = new_engine
    request.app.state.trades = []

    return ResetResponse(message="Matching engine reset successfully")


@router.get("/summary")
def get_summary(engine: MatchingEngineDep) -> list[SummaryLevel]:
    summary_lf = engine.unprocessed_orders.summary()
    df = summary_lf.collect()
    records = df.to_dicts()

    summary_res = [
        SummaryLevel(side=SideStr(r["side"]), price=float(r["price"]), size=float(r["size"]), count=int(r["count"]))
        for r in records
    ]
    return summary_res
