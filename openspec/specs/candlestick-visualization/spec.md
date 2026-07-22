# Capability: Candlestick Visualization

## Purpose

This capability provides OHLC (Open, High, Low, Close) candlestick chart visualization for trade data in the web dashboard. Users can select different time intervals, interact with historical price data, and analyze market movements through standard financial charting features.

## Requirements

### Requirement: Display candlestick chart
The frontend dashboard SHALL display an OHLC (Open, High, Low, Close) candlestick chart showing price evolution over time for trades executed in the current session.

#### Scenario: Chart displays trade data
- **WHEN** at least one trade has been executed in the session
- **THEN** the candlestick chart displays price candles aggregated by the selected time interval

#### Scenario: Chart shows empty state
- **WHEN** no trades have been executed yet
- **THEN** the chart displays an empty state message indicating no data is available

#### Scenario: Chart updates on refresh
- **WHEN** the dashboard refresh cycle polls new trade data (every 1 second)
- **THEN** the candlestick chart recomputes OHLC data and updates the visualization

### Requirement: Time interval selection
The system SHALL allow users to select different time bucket intervals for candlestick aggregation.

#### Scenario: User selects 5-second interval
- **WHEN** user selects the "5s" interval option
- **THEN** trades are aggregated into 5-second time buckets
- **THEN** each candle represents OHLC data for a 5-second period

#### Scenario: User selects 15-second interval
- **WHEN** user selects the "15s" interval option
- **THEN** trades are aggregated into 15-second time buckets
- **THEN** each candle represents OHLC data for a 15-second period

#### Scenario: User selects 30-second interval
- **WHEN** user selects the "30s" interval option
- **THEN** trades are aggregated into 30-second time buckets
- **THEN** each candle represents OHLC data for a 30-second period

#### Scenario: User selects 1-minute interval
- **WHEN** user selects the "1m" interval option
- **THEN** trades are aggregated into 1-minute time buckets
- **THEN** each candle represents OHLC data for a 1-minute period

#### Scenario: Default interval on load
- **WHEN** the dashboard loads for the first time
- **THEN** the candlestick chart defaults to 5-second intervals

### Requirement: OHLC computation
The system SHALL compute Open, High, Low, and Close prices for each time bucket from trade data.

#### Scenario: Single trade in bucket
- **WHEN** a time bucket contains exactly one trade at price P
- **THEN** Open = P, High = P, Low = P, Close = P

#### Scenario: Multiple trades in bucket
- **WHEN** a time bucket contains trades at prices [100, 102, 99, 101] in chronological order
- **THEN** Open = 100 (first trade price)
- **THEN** High = 102 (maximum price)
- **THEN** Low = 99 (minimum price)
- **THEN** Close = 101 (last trade price)

#### Scenario: Empty time buckets are skipped
- **WHEN** a time bucket contains no trades
- **THEN** no candle is rendered for that time bucket

### Requirement: Tab toggle interface
The dashboard SHALL provide a tab toggle to switch between the depth chart and candlestick chart views.

#### Scenario: User switches to candlestick view
- **WHEN** user clicks the "Candlesticks" tab
- **THEN** the depth chart is hidden
- **THEN** the candlestick chart is displayed

#### Scenario: User switches to depth chart view
- **WHEN** user clicks the "Depth Chart" tab (or "Market Depth" tab)
- **THEN** the candlestick chart is hidden
- **THEN** the depth chart is displayed

#### Scenario: Default view on load
- **WHEN** the dashboard loads for the first time
- **THEN** the depth chart view is displayed by default
- **THEN** the candlestick tab is available but not active

### Requirement: Interactive chart features
The candlestick chart SHALL support standard financial chart interactions for exploring historical price data.

#### Scenario: Tooltip on hover
- **WHEN** user hovers over a candlestick
- **THEN** a tooltip displays the candle's timestamp, Open, High, Low, and Close prices

#### Scenario: Crosshair tracking
- **WHEN** user moves mouse over the chart
- **THEN** a crosshair cursor tracks the mouse position with price and time labels

#### Scenario: Zoom via scroll
- **WHEN** user scrolls with mouse wheel over the chart
- **THEN** the chart zooms in or out on the time axis

#### Scenario: Pan via drag
- **WHEN** user clicks and drags on the chart
- **THEN** the chart pans left or right along the time axis

### Requirement: Visual styling
The candlestick chart SHALL use a dark theme consistent with the existing dashboard aesthetic.

#### Scenario: Bullish candles
- **WHEN** a candle's close price is greater than or equal to its open price (close >= open)
- **THEN** the candle body is rendered in green or an ascending color

#### Scenario: Bearish candles
- **WHEN** a candle's close price is less than its open price (close < open)
- **THEN** the candle body is rendered in red or a descending color

#### Scenario: Chart background and text
- **WHEN** the candlestick chart is rendered
- **THEN** the background color matches the dashboard's dark theme
- **THEN** axis labels, grid lines, and text use light colors for readability

### Requirement: Chart responsiveness
The candlestick chart SHALL adapt to the available container width and maintain a fixed aspect ratio.

#### Scenario: Container width change
- **WHEN** the browser window is resized
- **THEN** the chart width adjusts to fill the available container space
- **THEN** candle spacing adjusts to maintain readability

#### Scenario: Fixed height
- **WHEN** the candlestick chart is rendered
- **THEN** the chart maintains a fixed height appropriate for the dashboard layout (approximately 240px to match depth chart)
