from typing import Any

from fastapi.testclient import TestClient


def test_cancel_order_successfully(client: TestClient, sample_limit_order: dict[str, Any]) -> None:
    # Place order
    client.post("/place", json={"orders": [sample_limit_order]})

    # Verify it is in book
    book_response = client.get("/orders")
    assert "order1" in [o["order_id"] for o in book_response.json()["bids"]["100.0"]]

    # Cancel order
    cancel_response = client.delete(f"/orders/{sample_limit_order['order_id']}")
    assert cancel_response.status_code == 200
    assert "cancelled successfully" in cancel_response.json()["message"]

    # Verify it is removed from book
    book_response = client.get("/orders")
    assert book_response.json()["bids"] == {}


def test_cancel_non_existent_order(client: TestClient) -> None:
    response = client.delete("/orders/nonexistent_id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_cancel_already_filled_order(client: TestClient, sample_limit_order: dict[str, Any]) -> None:
    # Place buy order
    client.post("/place", json={"orders": [sample_limit_order]})

    # Place crossing sell order to fill it completely
    sell_order = sample_limit_order.copy()
    sell_order["order_id"] = "order2"
    sell_order["side"] = "SELL"
    sell_order["price"] = 90.0
    client.post("/place", json={"orders": [sell_order]})

    # Trigger match explicitly to fill the orders
    match_response = client.post("/match", json={"timestamp": sample_limit_order["timestamp"]})
    assert match_response.status_code == 200

    # Try to cancel the now-filled buy order
    response = client.delete(f"/orders/{sample_limit_order['order_id']}")
    assert response.status_code == 404
