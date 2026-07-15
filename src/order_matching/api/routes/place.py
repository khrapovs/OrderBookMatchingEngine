from fastapi import APIRouter, HTTPException, status

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import domain_order_to_response, request_to_domain_order
from order_matching.api.models.requests import PlaceRequest
from order_matching.api.models.responses import PlaceResponse
from order_matching.orders import Orders

router = APIRouter()


@router.post("/place")
def place(payload: PlaceRequest, engine: MatchingEngineDep) -> PlaceResponse:
    if not payload.orders:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="At least one order must be provided"
        )

    # 15.2 Check for duplicate IDs in the request itself
    request_ids = [order.order_id for order in payload.orders]
    if len(request_ids) != len(set(request_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate order ID in request")

    # Check if any ID already exists in the engine's active orders
    for order in payload.orders:
        if engine.unprocessed_orders.find_order_by_id(order.order_id) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Duplicate order ID: {order.order_id}")

    # Convert request orders to domain Orders
    domain_orders_list = [request_to_domain_order(o) for o in payload.orders]
    domain_orders = Orders(domain_orders_list)

    # Call matching_engine.place() with orders
    try:
        engine.place(orders=domain_orders)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return PlaceResponse(
        message=f"Successfully placed {len(payload.orders)} orders",
        orders=[domain_order_to_response(o) for o in domain_orders.orders],
    )
