## Why

The frontend dashboard currently shows real-time order book depth and recent trades, but lacks a way to visualize how market prices evolve over time during simulation runs. Users running the noise trader simulation need to see price trends and patterns as they emerge, not just individual trade snapshots. A candlestick chart provides the standard visualization for understanding market dynamics during simulated trading sessions.

## What Changes

- Add candlestick (OHLC) chart visualization to the frontend dashboard
- Implement time-bucket aggregation (5s, 15s, 30s, 1m intervals) for trade data
- Create tab toggle UI between existing Depth Chart and new Candlestick Chart views
- Integrate Lightweight Charts library (TradingView) for professional rendering
- Wire chart updates into existing dashboard refresh cycle
- Apply dark theme styling consistent with current UI aesthetic

**No backend changes required** - aggregation happens client-side from existing `/trades` endpoint.

## Capabilities

### New Capabilities

- `candlestick-visualization`: Frontend OHLC chart showing price evolution over configurable time intervals for simulation monitoring

### Modified Capabilities

<!-- No existing capabilities are being modified -->

## Impact

**Affected Files:**
- `src/order_matching/api/static/index.html` - Add tab UI and candlestick container
- `src/order_matching/api/static/candlestick.js` - New module for OHLC computation and chart rendering
- `src/order_matching/api/static/app.js` - Wire candlestick updates into refresh loop
- `src/order_matching/api/static/styles.css` - Tab styling and chart theming

**Dependencies:**
- Lightweight Charts library (TradingView) via CDN - ~50KB gzipped

**User Impact:**
- Simulation users gain price trend visualization
- Manual trading users can continue using existing depth chart view
- No breaking changes - new feature is additive
