from fastapi import APIRouter, Request

from order_matching.api.models.requests import ResetRequest
from order_matching.api.models.responses import ResetResponse
from order_matching.matching_engine import MatchingEngine

router = APIRouter()


@router.post("/reset")
def reset_engine(request: Request, payload: ResetRequest) -> ResetResponse:
    # Reinitialize engine in app state
    new_engine = MatchingEngine(seed=payload.seed)
    request.app.state.engine = new_engine
    request.app.state.trades = []

    return ResetResponse(message="Matching engine reset successfully")
