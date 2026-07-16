from fastapi import APIRouter
from loguru import logger

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.api.models.converters import domain_order_to_response
from order_matching.api.models.responses import OrderBookResponse

router = APIRouter()


@router.get("/orders")
def get_order_book(engine: MatchingEngineDep) -> OrderBookResponse:
    bids = {}
    for price, orders in engine.unprocessed_orders.bids.items():
        bids[price] = [domain_order_to_response(o) for o in orders.orders]

    offers = {}
    for price, orders in engine.unprocessed_orders.offers.items():
        offers[price] = [domain_order_to_response(o) for o in orders.orders]

    logger.debug(f"Produced order book with {len(bids)} bids and {len(offers)} offers")
    return OrderBookResponse(bids=bids, offers=offers)
