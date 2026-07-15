from fastapi import APIRouter, HTTPException, Request

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import domain_order_to_response, request_to_domain_order
from order_matching.api.models.requests import PlaceOrdersRequest
from order_matching.api.models.responses import PlaceOrdersResponse
from order_matching.orders import Orders

router = APIRouter()


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
        if engine.unprocessed_orders.find_order_by_id(order.order_id) is not None:
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
