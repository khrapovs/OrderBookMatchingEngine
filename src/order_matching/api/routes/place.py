from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import domain_order_to_response, request_to_domain_order
from order_matching.api.models.requests import PlaceRequest
from order_matching.api.models.responses import PlaceResponse
from order_matching.orders import Orders

router = APIRouter()


@router.post("/place")
def place(
    *,
    payload: Annotated[PlaceRequest, Body(openapi_examples=PlaceRequest.model_json_schema()["openapi_examples"])],
    engine: MatchingEngineDep,
) -> PlaceResponse:
    domain_orders = Orders(orders=[request_to_domain_order(o) for o in payload.orders])
    try:
        engine.place(orders=domain_orders)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return PlaceResponse(
        message=f"Successfully placed {len(payload.orders)} orders",
        orders=[domain_order_to_response(o) for o in domain_orders.orders],
    )
