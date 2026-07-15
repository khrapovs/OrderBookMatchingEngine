## Why

Currently, placing orders via the `POST /orders` endpoint immediately triggers matching by calling the matching engine's `match` method. This couples order placement and order matching, violating the requirement that placing orders should add them to the order book without triggering matching. Completely separating these two actions allows clients to build up an order book and control exactly when matching executes via the `POST /match` endpoint.

## What Changes

- Add a new public method `place(orders: Orders)` to the `MatchingEngine` class to append orders to the book and queue them for matching without triggering matching.
- Remove matching logic from the `POST /orders` API route, calling the new `place` method instead of `match`.
- Remove the accumulation/return of executed trades from the `POST /orders` endpoint.
- Update matching engine's `match` method to correctly match already-placed orders in the book without duplicating them or leaving fully-filled orders behind.

## Capabilities

### New Capabilities

*None*

### Modified Capabilities

- `fastapi-server`: Remove matching logic from Place Orders endpoint and ensure it is executed exclusively via Trigger Matching.

## Impact

- **API Layer**: `POST /orders` will no longer match orders or return/accumulate executed trades.
- **Core Logic**: `MatchingEngine` class will have a new public method `place`. The `match` method will process queued/placed orders.
- **Tests**: API and integration tests that expect immediate matching upon placing orders will need to be updated to explicitly call the match endpoint.
