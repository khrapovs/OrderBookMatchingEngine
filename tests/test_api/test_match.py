from datetime import datetime, timedelta
from typing import Any

from fastapi.testclient import TestClient


def test_match_empty_order_book(client: TestClient, sample_timestamp: datetime) -> None:
    response = client.post("/match", json={"timestamp": sample_timestamp.isoformat()})
    assert response.status_code == 200
    data = response.json()
    assert data["trades"] == []


def test_match_non_crossing_orders(
    client: TestClient, sample_timestamp: datetime, sample_limit_order: dict[str, Any]
) -> None:
    # Place a buy order at 100
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place a sell order at 110 (does not cross)
    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "order2"
    sell_order["side"] = "SELL"
    sell_order["price"] = 110.0
    client.post("/place", json={"orders": [sell_order]})

    # Match
    response = client.post("/match", json={"timestamp": sample_timestamp.isoformat()})
    assert response.status_code == 200
    assert response.json()["trades"] == []

    # Get order book to verify orders are still there
    book_response = client.get("/orders")
    assert len(book_response.json()["bids"]) == 1
    assert len(book_response.json()["offers"]) == 1


def test_match_crossing_orders(client: TestClient, sample_limit_order: dict[str, Any]) -> None:
    # Place a buy order at 100
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place a sell order at 95 (crosses)
    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "order2"
    sell_order["side"] = "SELL"
    sell_order["price"] = 95.0

    response = client.post("/place", json={"orders": [sell_order]})
    assert response.status_code == 200

    # Trigger match explicitly
    match_response = client.post("/match", json={"timestamp": sample_limit_order["timestamp"]})
    assert match_response.status_code == 200

    # Check trades accumulated
    trades_response = client.get("/trades")
    trades = trades_response.json()["trades"]
    assert len(trades) == 1
    trade = trades[0]
    assert trade["price"] == 100.0
    assert trade["size"] == 10.0
    assert trade["incoming_order_id"] == "order2"
    assert trade["book_order_id"] == "order1"


def test_match_timestamp_used_in_trades(
    client: TestClient, sample_timestamp: datetime, sample_limit_order: dict[str, Any]
) -> None:
    # Place buy order
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place crossing sell order
    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "order2"
    sell_order["side"] = "SELL"
    sell_order["price"] = 90.0
    client.post("/place", json={"orders": [sell_order]})

    # Trigger match explicitly
    match_response = client.post("/match", json={"timestamp": sample_timestamp.isoformat()})
    assert match_response.status_code == 200

    # Verify that the trade timestamp is the order/match timestamp
    trades_response = client.get("/trades")
    trades = trades_response.json()["trades"]
    assert len(trades) == 1
    assert trades[0]["timestamp"].startswith(sample_timestamp.isoformat())


def test_match_expired_orders(
    client: TestClient, sample_timestamp: datetime, sample_limit_order: dict[str, Any]
) -> None:
    # Place buy order with expiration
    expiration = sample_timestamp + timedelta(seconds=10)
    order = sample_limit_order.copy()
    order["expiration"] = expiration.isoformat()
    client.post("/place", json={"orders": [order]})

    # Match at a timestamp after expiration
    match_time = sample_timestamp + timedelta(seconds=15)
    response = client.post("/match", json={"timestamp": match_time.isoformat()})
    assert response.status_code == 200

    # Verify book is empty now (expired order cancelled)
    book_response = client.get("/orders")
    assert book_response.json()["bids"] == {}
    assert book_response.json()["offers"] == {}


def test_partial_fills(client: TestClient, sample_limit_order: dict[str, Any]) -> None:
    # Place buy order of size 10.0
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place sell order of size 4.0 at crossing price
    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "order2"
    sell_order["side"] = "SELL"
    sell_order["price"] = 90.0
    sell_order["size"] = 4.0

    client.post("/place", json={"orders": [sell_order]})

    # Trigger match explicitly
    match_response = client.post("/match", json={"timestamp": sample_limit_order["timestamp"]})
    assert match_response.status_code == 200

    # Check that remaining size of buy order in book is 6.0
    book_response = client.get("/orders")
    bids = book_response.json()["bids"]
    assert "100.0" in bids
    assert len(bids["100.0"]) == 1
    assert bids["100.0"][0]["size"] == 6.0
