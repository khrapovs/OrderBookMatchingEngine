## ADDED Requirements

### Requirement: Dual chart simultaneous display
The dashboard SHALL display the Candlestick chart and Market Depth chart simultaneously in a dedicated top visualization grid.

#### Scenario: Concurrent chart rendering
- **WHEN** the dashboard loads or receives polled market state updates
- **THEN** both the Candlestick chart and the Market Depth chart are rendered and updated concurrently without requiring tab switches

#### Scenario: Two-to-one aspect width ratio
- **WHEN** displayed on viewports with width greater than or equal to 1024px
- **THEN** the Candlestick chart occupies two-thirds (2fr) of the top visualization band width
- **THEN** the Market Depth chart occupies one-third (1fr) of the top visualization band width

#### Scenario: Responsive stacking on small viewports
- **WHEN** displayed on viewports with width less than 1024px
- **THEN** the Candlestick chart and Market Depth chart stack vertically in full width

## REMOVED Requirements

### Requirement: Tab toggle interface
**Reason**: Tab navigation is replaced by simultaneous dual-chart display in the top visualization row.
**Migration**: Remove tab toggle buttons and CSS display hiding; both charts remain permanently visible in the layout.
