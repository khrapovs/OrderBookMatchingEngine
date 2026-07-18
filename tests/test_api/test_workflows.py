from datetime import datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient


def test_complete_workflow(*, client: TestClient, sample_limit_order: dict[str, Any]) -> None:
    # 1. Reset engine
    client.post("/reset", json={})

    # 2. Place some non-crossing orders
    buy_order = sample_limit_order.copy()
    buy_order["order_id"] = "buy_1"
    buy_order["price"] = 100.0
    buy_order["size"] = 10.0
    client.post("/place", json={"orders": [buy_order]})

    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "sell_1"
    sell_order["side"] = "SELL"
    sell_order["price"] = 105.0
    sell_order["size"] = 5.0
    client.post("/place", json={"orders": [sell_order]})

    # 3. View order book
    book = client.get("/orders").json()
    assert len(book["bids"]) == 1
    assert len(book["offers"]) == 1

    # 4. Place a crossing order that executes a trade
    crossing_sell = sample_limit_order.copy()
    crossing_sell["order_id"] = "sell_2"
    crossing_sell["side"] = "SELL"
    crossing_sell["price"] = 99.0
    crossing_sell["size"] = 4.0
    client.post("/place", json={"orders": [crossing_sell]})

    # Trigger match explicitly
    match_response = client.post("/match", json={"timestamp": sample_limit_order["timestamp"]})
    assert match_response.status_code == 200

    # 5. Check trades
    trades = client.get("/trades").json()["trades"]
    assert len(trades) == 1
    assert trades[0]["price"] == 100.0
    assert trades[0]["size"] == 4.0

    # 6. Verify remaining buy size in book
    book_after = client.get("/orders").json()
    assert book_after["bids"]["100.0"][0]["size"] == 6.0


def test_backtesting_scenario(
    *, client: TestClient, sample_timestamp: datetime, sample_limit_order: dict[str, Any]
) -> None:
    # Simulate historical backtesting with exact timestamps
    t0 = sample_timestamp

    # Place buy order at t0
    buy_order = sample_limit_order.copy()
    buy_order["order_id"] = "buy"
    buy_order["price"] = 10.0
    buy_order["size"] = 100.0
    buy_order["timestamp"] = t0.isoformat()
    client.post("/place", json={"orders": [buy_order]})

    # Place crossing sell order at t0 + 1 hour
    t1 = t0 + timedelta(hours=1)
    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "sell"
    sell_order["side"] = "SELL"
    sell_order["price"] = 10.0
    sell_order["size"] = 100.0
    sell_order["timestamp"] = t1.isoformat()
    client.post("/place", json={"orders": [sell_order]})

    # Trigger match explicitly
    match_response = client.post("/match", json={"timestamp": t1.isoformat()})
    assert match_response.status_code == 200

    # Check trades and check that the trade timestamp matches t1
    trades = client.get("/trades").json()["trades"]
    assert len(trades) == 1
    assert trades[0]["timestamp"].startswith(t1.isoformat())
