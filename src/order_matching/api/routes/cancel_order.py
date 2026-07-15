from dataclasses import replace

from fastapi import APIRouter, HTTPException

from order_matching.api.dependencies import MatchingEngineDep
from order_matching.orders import Orders
from order_matching.status import Status

router = APIRouter()


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
