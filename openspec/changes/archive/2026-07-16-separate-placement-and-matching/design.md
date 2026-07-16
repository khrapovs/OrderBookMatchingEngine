## Context

The matching engine currently executes matching logic immediately whenever an order is submitted to the `POST /orders` endpoint. This couples placement and matching. Per the `fastapi-server` specification, the POST `/orders` endpoint is expected to simply add orders to the book without matching, and a separate POST `/match` endpoint is expected to trigger matching.

## Goals / Non-Goals

**Goals:**
- Add `place(orders: Orders)` to `MatchingEngine` to place orders into `unprocessed_orders` and queue them in `self._queue`.
- Update `POST /orders` endpoint to use `place` and return placed orders with no trades.
- Ensure that calling `engine.match(timestamp)` matches already-placed orders in the book.
- Ensure that fully filled orders are removed from the book.
- All unit, integration, and API tests continue to pass (with updates to expect asynchronous matching).

**Non-Goals:**
- Adding persistent database storage for orders.
- Rewriting the core matching logic (`_match` and `_execute_trades`).

## Decisions

### 1. Removing orders from the book before calling `_match`
- **Option A**: Update `_match` to handle incoming orders that are already in `unprocessed_orders` without duplicating them and removing them when fully filled. This would require rewriting complex price-time queue operations inside `unprocessed_orders.append` and `_execute_trades_for_one_price`.
- **Option B (Chosen)**: In the main `match` loop, for each order dequeued from `self._queue`, check if it exists in the order book. If it does and is not a cancellation order, temporarily remove it from the book before matching. The existing `_match` method will naturally match it, execute trades, and append any remaining size back to the book.
- **Rationale**: Option B is extremely clean, maintains the invariants of the original code, and avoids potential bugs/complexities in changing the core matching algorithm.

### 2. Validating duplicate order IDs in `place`
- **Option A**: Perform all validation in the API layer.
- **Option B (Chosen)**: Perform validation in both the API layer and the `MatchingEngine.place` method (raising `ValueError` if an ID is already in the order book or if the batch contains duplicate IDs).
- **Rationale**: Keeps the core logic robust and consistent with other methods like `cancel_order` that raise `ValueError`.

## Risks / Trade-offs

- **Risk**: Dequeuing and temporarily removing an order from the book might be slow if the book is very large.
- **Mitigation**: Ripgrep searches show that order lookup in `unprocessed_orders` uses dictionary lookups for prices and quick iteration. This is fast enough for the target workflows.
