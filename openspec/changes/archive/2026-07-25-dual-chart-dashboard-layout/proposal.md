## Why

The current web dashboard uses a tab toggle that forces users to choose between viewing either the Market Depth chart or the Candlestick chart. Traders and developers monitoring the matching engine need to observe live market depth (liquidity profile) and price action history (OHLC candles) simultaneously to evaluate market behavior effectively.

## What Changes

- **Dual Chart Display**: Remove the tabbed navigation so both the Candlestick chart and Market Depth chart are displayed at the same time on the dashboard.
- **Top Section Banner (2:1 Ratio)**: Position both charts side-by-side in a dedicated top visualization band across the dashboard width, assigning a 2:1 width ratio (2fr for Candlestick, 1fr for Depth).
- **Responsive Layout**: On wide viewports ($\ge 1024\text{px}$), charts are side-by-side in a 2:1 ratio. On smaller screens, charts stack vertically. The operational grid (controls, order book tables, lists) sits directly below the chart band.
- **Removal of Tab Toggle**: Remove tab switching logic and buttons, rendering both charts concurrently on every polling tick.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `candlestick-visualization`: Replace tab toggle requirements with simultaneous dual-chart layout requirements.
- `frontend-ui`: Update visual hierarchy to feature a 2:1 top visualization band above operational controls and lists.

## Impact

- `src/order_matching/api/static/index.html`: Restructure top DOM elements into `.charts-grid` (Candlestick + Depth) and `.dashboard-grid` (Controls + Order Book + Lists).
- `src/order_matching/api/static/styles.css`: Add styles for `.charts-grid` 2:1 grid layout and responsive breakpoints.
- `src/order_matching/api/static/app.js`: Remove tab switching logic; refresh both charts on polling update.
- `src/order_matching/api/static/ui.js` & `chart.js`: Move spread indicator reference to the Depth panel header.
