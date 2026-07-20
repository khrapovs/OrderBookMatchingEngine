from collections.abc import Iterator
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient

from order_matching.api.app import app
from order_matching.api.utils import create_market
from order_matching.executed_trades import ExecutedTrades


@pytest.fixture
def client() -> Iterator[TestClient]:
    # Reset application state for each test to guarantee isolation
    app.state.market = create_market(traders=[], seed=42)
    app.state.trades = ExecutedTrades()
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_timestamp() -> datetime:
    return datetime(2023, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_limit_order(sample_timestamp: datetime) -> dict[str, Any]:
    return {
        "order_type": "limit",
        "order_id": "order1",
        "trader_id": "trader1",
        "side": "BUY",
        "size": 10.0,
        "price": 100.0,
        "timestamp": sample_timestamp.isoformat(),
    }


@pytest.fixture
def sample_market_order(sample_timestamp: datetime) -> dict[str, Any]:
    return {
        "order_type": "market",
        "order_id": "order2",
        "trader_id": "trader2",
        "side": "SELL",
        "size": 5.0,
        "timestamp": sample_timestamp.isoformat(),
    }
