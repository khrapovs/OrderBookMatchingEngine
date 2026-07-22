## 1. Add Lightweight Charts Library

- [x] 1.1 Add Lightweight Charts CDN script tag to index.html with integrity hash
- [x] 1.2 Position script tag before existing module scripts to ensure library loads first

## 2. Create Candlestick Module

- [x] 2.1 Create new candlestick.js file in static/ directory
- [x] 2.2 Implement computeCandles(trades, intervalSeconds) function to aggregate trades into OHLC buckets
- [x] 2.3 Implement initCandlestickChart(container) function to initialize Lightweight Charts instance
- [x] 2.4 Implement renderCandlestickChart(candles) function to update chart with new data
- [x] 2.5 Implement setupIntervalSelector() to handle time interval button clicks
- [x] 2.6 Add dark theme configuration for chart (background, text colors, grid lines)
- [x] 2.7 Export public functions for use by app.js

## 3. Update HTML Structure

- [x] 3.1 Add tab toggle UI above depth chart with "Market Depth" and "Candlesticks" tabs
- [x] 3.2 Create new candlestick-chart-container div alongside depth-chart-wrapper
- [x] 3.3 Add interval selector buttons (5s, 15s, 30s, 1m) in candlestick panel header
- [x] 3.4 Add candlestick chart empty state message div
- [x] 3.5 Update panel-header structure to support tab toggle

## 4. Wire into Dashboard Refresh

- [x] 4.1 Import candlestick module functions in app.js
- [x] 4.2 Initialize candlestick chart in DOMContentLoaded event handler
- [x] 4.3 Add candlestick chart update call to refreshDashboard() function
- [x] 4.4 Pass trade data from fetchMarketState() to candlestick renderer
- [x] 4.5 Implement tab toggle logic to show/hide depth chart vs candlestick chart

## 5. Style Candlestick UI

- [x] 5.1 Add CSS for tab toggle buttons (active/inactive states)
- [x] 5.2 Add CSS for candlestick container layout and sizing
- [x] 5.3 Add CSS for interval selector buttons (active/inactive states)
- [x] 5.4 Add CSS for candlestick empty state message
- [x] 5.5 Ensure chart container has fixed height matching depth chart (~240px)
- [x] 5.6 Add responsive width styling for chart container

## 6. Testing and Refinement

- [x] 6.1 Test candlestick chart with manual trade placement (sparse data)
- [x] 6.2 Test candlestick chart with simulation running (continuous data)
- [x] 6.3 Verify all interval options (5s, 15s, 30s, 1m) compute OHLC correctly
- [x] 6.4 Verify tab toggle switches between depth and candlestick views
- [x] 6.5 Verify chart tooltip shows correct OHLC values on hover
- [x] 6.6 Verify chart zoom and pan interactions work smoothly
- [x] 6.7 Verify dark theme colors match existing dashboard aesthetic
- [x] 6.8 Test empty state displays when no trades exist
