# Architecture

## Core Sections (Required)

### 1) Architectural Style

- Primary style: Domain-driven, data-centric library with central stateful engine
- Why this classification: Code is organized around domain concepts (Order, Trade, OrderBook, MatchingEngine) rather than layers or features. The MatchingEngine maintains state (order book, queue) and orchestrates matching logic. No HTTP/service layer—this is a library consumed by other applications.
- Primary constraints:
  1. Must maintain price-time priority for order matching
  2. Immutable trade history (trades never modified once executed)
  3. Optional polars dependency for data export (must work without it)

### 2) System Flow

```text
User code -> MatchingEngine.match(orders, timestamp)
  -> Queue incoming orders + expired orders
  -> For each order: check matching conditions
    -> If match exists: execute trades (price-time priority)
      -> Update order sizes, create Trade objects
      -> Remove filled orders from OrderBook
    -> If no match: add order to OrderBook
  -> Return ExecutedTrades collection
```

Detailed flow (with file evidence):
1. **Entry**: User instantiates `MatchingEngine(seed)` and calls `match(orders, timestamp)` (`matching_engine.py` line 51)
2. **Queue preparation**: Incoming orders + expired orders from `OrderBook` added to internal queue (`matching_engine.py` lines 67-68)
3. **Order processing loop**: While queue not empty, dequeue and match each order (`matching_engine.py` lines 70-72)
4. **Matching decision**: Check if order status is CANCEL (remove from book), or if matching order exists (execute trades), or else add to book (`matching_engine.py` lines 84-92)
5. **Trade execution**: For matching orders, iterate through opposite side prices in price-time priority, execute trades, update order sizes (`matching_engine.py` lines 94-134)
6. **Result**: Return `ExecutedTrades` object containing all trades executed in this matching round (`matching_engine.py` line 72)

### 3) Layer/Module Responsibilities

| Layer or module | Owns | Must not own | Evidence |
|-----------------|------|--------------|----------|
| MatchingEngine | Order matching orchestration, queue management, trade execution coordination, expiration handling | Order book data structure details, trade/order data schemas | matching_engine.py |
| OrderBook | Bid/offer storage by price level, order indexing by expiration, order book summary generation, imbalance calculation | Matching logic, trade execution | order_book.py |
| Order/LimitOrder/MarketOrder | Order data models, price rounding, order type behavior (limit vs market pricing) | Matching logic, storage | order.py |
| Orders | Order collection management (queue operations: add, remove, dequeue) | Individual order state, matching logic | orders.py |
| ExecutedTrades | Trade collection storage indexed by timestamp, trade aggregation | Order matching, order book state | executed_trades.py |
| Trade | Individual trade record (immutable) | Trade execution logic, aggregation | trade.py |
| PolarsExporter | Conversion from Orders/ExecutedTrades to polars LazyFrame with schema validation | Core matching logic, order book operations | exporters/polars.py |
| Schemas | Pandera schema definitions for data validation (OrderData, TradeData, OrderBookSummary) | Business logic, matching rules | schemas.py |

### 4) Reused Patterns

| Pattern | Where found | Why it exists |
|---------|-------------|---------------|
| Dataclass | Order, LimitOrder, MarketOrder, Trade | Immutable data models with type hints and automatic initialization |
| Collection wrapper | Orders, ExecutedTrades | Encapsulate list/dict operations with domain-specific methods (e.g., dequeue, add by timestamp) |
| Strategy (implicit) | LimitOrder vs MarketOrder price setting | Market orders use infinity/-infinity pricing, limit orders use user-specified price (order.py lines 28-44) |
| Dictionary indexing | OrderBook.bids, OrderBook.offers (dict[float, Orders]), orders_by_expiration (dict[datetime, Orders]) | Fast lookup by price level and expiration time for matching (order_book.py lines 20-22) |
| Exporter abstraction | Exporter base class, PolarsExporter subclass | Optional data export without coupling core logic to polars (exporters/base.py, exporters/polars.py) |
| Faker for IDs | get_faker(seed) in MatchingEngine | Deterministic UUID generation for trades (matching_engine.py line 46, line 130) |

### 5) Known Architectural Risks

- **State mutation during iteration**: MatchingEngine modifies order sizes and removes orders from OrderBook during iteration over price levels. Carefully managed but could lead to bugs if iteration logic changes (matching_engine.py lines 102-118)
- **Polars dependency leak**: order_book.py imports polars/pandera unconditionally even though polars is optional. This breaks the optional dependency model. (order_book.py lines 5-6)
- **No persistence layer**: MatchingEngine keeps order book in memory; no save/restore mechanism. Users must manage state externally if needed.
- **No concurrency safety**: MatchingEngine is not thread-safe. Concurrent match() calls would corrupt order book state.

### 6) Evidence

- src/order_matching/matching_engine.py
- src/order_matching/order_book.py
- src/order_matching/order.py
- src/order_matching/orders.py
- src/order_matching/executed_trades.py
- src/order_matching/trade.py
- src/order_matching/exporters/polars.py
- src/order_matching/schemas.py
