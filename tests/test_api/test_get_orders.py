from typing import Any

from fastapi.testclient import TestClient


def test_get_empty_order_book(client: TestClient) -> None:
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json()["bids"] == {}
    assert response.json()["offers"] == {}


def test_get_order_book_bids_only(client: TestClient, *, sample_limit_order: dict[str, Any]) -> None:
    client.post("/place", json={"orders": [sample_limit_order]})
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()["bids"]) == 1
    assert response.json()["offers"] == {}


def test_get_order_book_offers_only(client: TestClient, *, sample_limit_order: dict[str, Any]) -> None:
    order = sample_limit_order.copy()
    order["side"] = "SELL"
    order["price"] = 200.0
    client.post("/place", json={"orders": [order]})

    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json()["bids"] == {}
    assert len(response.json()["offers"]) == 1


def test_get_order_book_mixed_and_grouped(client: TestClient, *, sample_limit_order: dict[str, Any]) -> None:
    # Place buy at 100
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place another buy at 100 with different ID
    order2 = sample_limit_order.copy()
    order2["order_id"] = "order2"
    client.post("/place", json={"orders": [order2]})

    # Place buy at 105
    order3 = sample_limit_order.copy()
    order3["order_id"] = "order3"
    order3["price"] = 105.0
    client.post("/place", json={"orders": [order3]})

    # Place sell at 200
    order4 = sample_limit_order.copy()
    order4["order_id"] = "order4"
    order4["side"] = "SELL"
    order4["price"] = 200.0
    client.post("/place", json={"orders": [order4]})

    response = client.get("/orders")
    assert response.status_code == 200
    bids = response.json()["bids"]
    offers = response.json()["offers"]

    assert len(bids) == 2
    assert len(bids["100.0"]) == 2
    assert len(bids["105.0"]) == 1
    assert len(offers) == 1
