## Context

The frontend dashboard currently uses three JavaScript modules:
- `app.js` - Main orchestration, polling loop, form handling
- `chart.js` - SVG-based depth chart rendering
- `ui.js` - DOM manipulation for tables and lists
- `api.js` - Fetch wrappers for backend endpoints

The market visualization section (middle column) currently shows:
1. Depth chart (price/volume histogram) - SVG-based
2. Aggregated order book tables (bids/asks)

Users run simulations with noise traders (Poisson arrivals at ~1.5s, ~3s, ~6s intervals) which generate continuous trade flow. The existing "Recent Trades" list shows individual trades but doesn't visualize price evolution over time.

**Constraints:**
- Frontend-only change (no backend modifications allowed)
- Must use existing `/trades` endpoint (returns `TradeResponse[]`)
- Dashboard refresh cycle is 1 second
- Dark theme consistency required
- No npm build system (static files served directly)

## Goals / Non-Goals

**Goals:**
- Visualize OHLC (Open/High/Low/Close) price data over configurable time buckets
- Support 5s, 15s, 30s, 1m interval selection for different zoom levels
- Integrate seamlessly into existing dashboard refresh cycle
- Provide professional charting UX (zoom, pan, crosshair, tooltips)
- Maintain UI consistency with current dark theme
- Keep implementation simple for v1

**Non-Goals:**
- Volume bars below candles (deferred to future iteration)
- Advanced technical indicators (moving averages, RSI, etc.)
- Historical data persistence beyond current session
- Backend endpoint for pre-aggregated OHLC data
- Real-time streaming updates (polling is sufficient)
- Mobile-optimized touch interactions

## Decisions

### Decision 1: Tab Toggle vs Separate Section

**Chosen: Tab toggle between Depth Chart and Candlestick Chart**

**Rationale:**
- Both are "market visualization" - serve similar purposes for different use cases
- Depth chart useful for manual trading (see current order pressure)
- Candlestick chart useful for simulation watching (see price trends)
- Avoids adding vertical scroll or shrinking existing components
- Users can quickly switch views based on their current task

**Alternatives considered:**
- *Add fourth column*: Too cramped on laptop screens, overkill for a visualization option
- *Replace trade list*: Trade list serves different purpose (activity log), shouldn't be replaced
- *Below depth chart*: Adds scroll, reduces visible space for both charts

### Decision 2: Frontend Aggregation vs Backend Endpoint

**Chosen: Frontend computes OHLC from `/trades` data**

**Rationale:**
- `/trades` endpoint already exists and returns all necessary data
- Aggregation logic is simple (~50 lines of JavaScript)
- Allows experimenting with different intervals without backend changes
- Trades dataset size is manageable (simulation sessions are short-lived)
- Avoids adding new route/model/converter boilerplate to backend

**Alternatives considered:**
- *New `/candles?interval=5s` endpoint*: More "correct" architecturally but adds backend complexity for marginal benefit
- *WebSocket streaming*: Overkill when polling already works fine

**Trade-offs:**
- Frontend does more computation (negligible with typical trade counts)
- Re-computes on every refresh (could optimize with incremental updates later)

### Decision 3: Lightweight Charts vs Pure SVG

**Chosen: Lightweight Charts library (TradingView)**

**Rationale:**
- Professional candlestick rendering out of the box
- Built-in zoom, pan, crosshair, tooltips, and time axis
- Used by real trading platforms - proven UX patterns
- ~50KB gzipped - acceptable for this use case
- CDN delivery (no build system required)
- Dark theme support built-in

**Alternatives considered:**
- *Pure SVG (like depth chart)*: Consistent with existing code but requires building zoom/pan/tooltip infrastructure (~300+ lines)
- *D3.js*: More flexible but steeper learning curve and larger bundle
- *Chart.js*: Good for general charts but not specialized for financial data

**Trade-offs:**
- External dependency (acceptable - loaded via CDN with integrity hash)
- Less customization than pure SVG (but default styling is excellent)

### Decision 4: Time Bucket Algorithm

**Chosen: Floor timestamps to interval boundaries**

```javascript
const bucketTime = Math.floor(timestamp / intervalSeconds) * intervalSeconds;
```

**Rationale:**
- Simple and deterministic
- Aligns buckets to wall-clock boundaries (e.g., 5s buckets align to :00, :05, :10, etc.)
- Easy to reason about when inspecting charts
- Standard approach used by financial charting systems

**Trade-offs:**
- First/last buckets might be partial if session doesn't align with interval
- Alternative (sliding windows) would be smoother but harder to understand

### Decision 5: Default Interval

**Chosen: 5 seconds**

**Rationale:**
- Given trader arrival rates (~1.5s, 3s, 6s), 5s buckets have good trade density
- Not too sparse (1s would have many empty buckets)
- Not too aggregated (30s would hide short-term dynamics)
- Can be changed by user via interval selector

## Risks / Trade-offs

### Risk: Empty candles with sparse data
**Scenario**: Manual trading mode produces infrequent trades, resulting in many empty time buckets.

**Mitigation**:
- Default to 5s interval which works well for simulation
- Provide interval selector so users can widen buckets (30s, 1m) if needed
- Chart gracefully handles missing data (Lightweight Charts skips empty buckets)

### Risk: Large trade datasets slow down frontend
**Scenario**: Very long simulation sessions accumulate thousands of trades, causing frontend aggregation to lag.

**Mitigation**:
- For v1, acceptable - typical sessions are short (<5 minutes)
- Future optimization: incremental OHLC updates (only process new trades since last refresh)
- Future optimization: backend `/candles` endpoint if needed

### Risk: Lightweight Charts CDN failure
**Scenario**: CDN becomes unavailable, chart doesn't load.

**Mitigation**:
- Use integrity hash (Subresource Integrity) to detect tampering
- Graceful degradation: show "Chart unavailable" message if library fails to load
- Future: vendor library locally if reliability becomes an issue

### Trade-off: No volume bars in v1
**Implication**: Users can't see trade volume patterns alongside price action.

**Justification**: Keeps v1 scope minimal. Volume can be added in future iteration with `volume` series below candles.

### Trade-off: Polling refresh, not real-time streaming
**Implication**: 1-second polling means chart updates in discrete jumps, not smoothly.

**Justification**: Existing architecture uses polling everywhere. Adding streaming just for candles is inconsistent. Acceptable for simulation visualization.

## Migration Plan

**Deployment:**
1. Add Lightweight Charts CDN script tag to `index.html` (before other scripts)
2. Deploy new `candlestick.js` module
3. Update `app.js` to wire candlestick refresh
4. Update `index.html` with tab UI
5. Deploy CSS updates

**No rollback needed** - purely additive frontend feature. If issues arise, users can simply ignore the new tab.

**No data migration** - operates on transient in-memory trade data.

## Open Questions

None - design is clear and implementation-ready.
