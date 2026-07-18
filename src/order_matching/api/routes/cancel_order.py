from fastapi import APIRouter, HTTPException, status

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.responses import CancelOrderResponse

router = APIRouter()


@router.delete("/orders/{order_id}")
def cancel_order(*, order_id: str, engine: MatchingEngineDep) -> CancelOrderResponse:
    try:
        engine.cancel_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CancelOrderResponse(message=f"Order {order_id} cancelled successfully")
