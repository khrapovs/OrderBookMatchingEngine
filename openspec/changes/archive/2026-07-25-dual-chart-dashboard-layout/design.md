## Context

The current dashboard embeds the Market Depth chart and Candlestick chart into a single panel inside Column 2 of the main dashboard grid. The two views are managed via a tab toggle interface where selecting one hides the other with CSS (`display: none`).

To allow traders to analyze both live liquidity (order depth) and historical price movement (OHLC candles) concurrently, we are refactoring the dashboard structure. We will move both charts into a top visualization section spanning the width of the dashboard with a 2:1 horizontal ratio.

## Goals / Non-Goals

**Goals:**
- Present both Candlestick Chart and Market Depth Chart concurrently on dashboard load and during live polling.
- Assign a 2:1 width ratio (2fr Candlesticks : 1fr Depth) on viewports $\ge 1024\text{px}$.
- Maintain responsive stacking behavior on mobile and tablet viewports.
- Keep the operational controls (Order Placement, Matching Controller) and market lists (Order Book, Outstanding Orders, Recent Trades) accessible directly below the charts.

**Non-Goals:**
- Changing underlying chart rendering libraries (Lightweight Charts for candlesticks and native SVG for depth chart remain as-is).
- Modifying FastAPI endpoints or backend data schemas.

## Decisions

### Decision 1: Create a Separate `.charts-grid` Section Above `.dashboard-grid`
- **Choice**: Separate the dashboard container into two main structural sections inside `<main>`:
  1. `<section class="charts-grid">`: Top row containing Candlestick and Depth chart panels in a 2:1 CSS Grid ratio.
  2. `<section class="dashboard-grid">`: Bottom 3-column operational grid containing Controls (Column 1), Level 2 Order Book Summary (Column 2), and Order/Trade Lists (Column 3).
- **Alternatives Considered**:
  - *Stacking inside Column 2*: Keeps 3 columns from top to bottom, but restricts candlestick chart width to ~33% of screen space.
  - *Full-width top section for all charts*: Moving all operational lists below charts. The chosen 2:1 top band layout provides optimal width for OHLC price action while keeping liquidity depth visible side-by-side.

### Decision 2: Permanent Concurrent Rendering in Polling Loop
- **Choice**: In `app.js`, remove tab click listeners and `switchChartTab` helper function. `refreshDashboard()` will call both `renderDepthChart(orderBook)` and `updateCandlestickChart()` on every 1-second polling tick.
- **Rationale**: Since both charts are mounted and visible in the DOM, running both render updates ensures zero delay when new trades execute or order book levels update.

### Decision 3: Move Spread Label to Depth Chart Header
- **Choice**: Move `#spread-value` from the depth labels bar into the Depth Chart panel header for immediate visibility alongside market depth.

## Risks / Trade-offs

- **[Risk] Chart Container Resize Delays**: Lightweight Charts canvas might not immediately fill resized 2fr container space on window resize.
  - **Mitigation**: `candlestick.js` uses `ResizeObserver` on `#candlestick-chart-container`, which automatically triggers `chart.applyOptions({ width })` whenever layout width shifts.

- **[Risk] Increased Vertical Page Height**: Having both charts plus operational tables increases vertical page length.
  - **Mitigation**: Page container permits clean vertical scrolling, and operational panels keep internal scrollbars (`.scrollable-body`) for long order/trade tables.
