from datetime import datetime

from order_matching.enums import Side
from order_matching.matching_engine import MatchingEngine
from order_matching.order import LimitOrder
from order_matching.orders import Orders


def prepopulate_engine(engine: MatchingEngine) -> MatchingEngine:
    """Prepopulate the matching engine with some initial non-crossing orders."""
    now = datetime.now()
    trader_id = "market_maker"
    orders = [
        # Bids (BUY)
        LimitOrder(side=Side.BUY, price=99.50, size=15.0, timestamp=now, order_id="init_buy_1", trader_id=trader_id),
        LimitOrder(side=Side.BUY, price=99.00, size=10.0, timestamp=now, order_id="init_buy_2", trader_id=trader_id),
        LimitOrder(side=Side.BUY, price=98.50, size=25.0, timestamp=now, order_id="init_buy_3", trader_id=trader_id),
        LimitOrder(side=Side.BUY, price=98.00, size=30.0, timestamp=now, order_id="init_buy_4", trader_id=trader_id),
        # Asks (SELL)
        LimitOrder(side=Side.SELL, price=100.50, size=12.0, timestamp=now, order_id="init_sell_1", trader_id=trader_id),
        LimitOrder(side=Side.SELL, price=101.00, size=8.0, timestamp=now, order_id="init_sell_2", trader_id=trader_id),
        LimitOrder(side=Side.SELL, price=101.50, size=22.0, timestamp=now, order_id="init_sell_3", trader_id=trader_id),
        LimitOrder(side=Side.SELL, price=102.00, size=28.0, timestamp=now, order_id="init_sell_4", trader_id=trader_id),
    ]
    engine.place(Orders(orders=orders))
    return engine
