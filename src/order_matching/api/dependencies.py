from typing import Annotated

from fastapi import Depends, Request

from order_matching.matching_engine import MatchingEngine


def get_matching_engine(request: Request) -> MatchingEngine:
    return request.app.state.market.engine


MatchingEngineDep = Annotated[MatchingEngine, Depends(get_matching_engine)]
