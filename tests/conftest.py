from datetime import datetime, timedelta

import numpy as np
import pytest

from order_matching.order import LimitOrder
from order_matching.orders import Orders
from order_matching.random import get_faker, get_random_generator
from order_matching.side import Side


@pytest.fixture
def random_orders() -> Orders:
    faker = get_faker()
    rng = get_random_generator(seed=42)
    orders_per_timestamp, number_of_time_points = 100, 10
    time_intervals = np.array(rng.uniform(low=0, high=1, size=number_of_time_points))
    random_timestamps = [datetime(2023, 1, 1) + timedelta(days=float(days)) for days in time_intervals.cumsum()]
    orders = list()
    for timestamp in random_timestamps:
        prices = rng.lognormal(mean=1, size=orders_per_timestamp).round(decimals=1)
        sizes = rng.lognormal(mean=1, size=orders_per_timestamp).round(decimals=4)
        sides = rng.choice([Side.SELL, Side.BUY], size=orders_per_timestamp)
        new_orders = [
            LimitOrder(
                side=side, price=price, size=size, timestamp=timestamp, order_id=faker.uuid4(), trader_id=faker.uuid4()
            )
            for side, price, size in zip(sides, prices, sizes, strict=True)
        ]
        orders.extend(new_orders)
    return Orders(orders)
