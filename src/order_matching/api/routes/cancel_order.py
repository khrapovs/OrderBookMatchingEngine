from fastapi import APIRouter, HTTPException

from order_matching.api.dependencies import MatchingEngineDep

router = APIRouter()


@router.delete("/orders/{order_id}")
def cancel_order(order_id: str, engine: MatchingEngineDep) -> dict[str, str]:
    try:
        engine.cancel_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"message": f"Order {order_id} cancelled successfully"}
