import json
import sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen


def call_api(method: str, path: str, data: dict | None = None) -> dict:
    url = f"http://127.0.0.1:8000{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None

    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error calling {method} {path}: {e}")
        print("Please make sure the API server is running at http://127.0.0.1:8000")
        sys.exit(1)


def main() -> None:
    print("=== Order Book API Backtesting Demo ===")

    # 1. Reset matching engine
    print("\n1. Resetting engine...")
    res = call_api("POST", "/reset", {"seed": 100})
    print(res["message"])

    # 2. Define historical timeline
    base_time = datetime(2023, 1, 1, 10, 0, 0)

    # Place initial orders
    print("\n2. Placing initial limit orders...")
    orders_payload = {
        "orders": [
            {
                "order_type": "limit",
                "order_id": "buy_1",
                "trader_id": "trader_a",
                "side": "BUY",
                "size": 10.0,
                "price": 100.0,
                "timestamp": base_time.isoformat(),
            },
            {
                "order_type": "limit",
                "order_id": "sell_1",
                "trader_id": "trader_b",
                "side": "SELL",
                "size": 5.0,
                "price": 105.0,
                "timestamp": base_time.isoformat(),
            },
        ]
    }
    call_api("POST", "/orders", orders_payload)

    # View current order book
    book = call_api("GET", "/orders")
    print(f"Current bids: {list(book['bids'].keys())}")
    print(f"Current offers: {list(book['offers'].keys())}")

    # 3. Simulate crossing order placed at t0 + 10 minutes
    print("\n3. Placing a crossing market order at T+10 minutes...")
    market_sell = {
        "orders": [
            {
                "order_type": "market",
                "order_id": "sell_market",
                "trader_id": "trader_c",
                "side": "SELL",
                "size": 3.0,
                "timestamp": (base_time + timedelta(minutes=10)).isoformat(),
            }
        ]
    }
    res_place = call_api("POST", "/orders", market_sell)
    print(res_place["message"])

    # Check trade history to verify execution
    trades = call_api("GET", "/trades")
    print(f"\nTrade History ({len(trades['trades'])} executed):")
    for t in trades["trades"]:
        print(
            f"  Trade ID: {t['trade_id'][:8]}... | "
            f"Price: {t['price']} | Size: {t['size']} | "
            f"Timestamp: {t['timestamp']}"
        )

    # 4. Show summary levels
    print("\n4. Getting aggregated summary levels:")
    summary = call_api("GET", "/summary")
    for level in summary:
        print(f"  Side: {level['side']} | Price: {level['price']} | Size: {level['size']} | Count: {level['count']}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
