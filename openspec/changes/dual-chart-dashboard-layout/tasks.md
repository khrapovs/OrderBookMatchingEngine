## 1. HTML Layout Restructuring

- [ ] 1.1 Restructure `index.html` main section to add `.charts-grid` containing Candlestick Chart (2fr) and Market Depth Chart (1fr)
- [ ] 1.2 Remove chart tab buttons (`.chart-tabs`) and simplify section headers
- [ ] 1.3 Move spread indicator element (`#spread-value`) into the Market Depth panel header

## 2. CSS Styling & Responsive Grid

- [ ] 2.1 Add `.charts-grid` styles with `grid-template-columns: 2fr 1fr` and gap styling in `styles.css`
- [ ] 2.2 Add media queries for responsive stacking on viewports under 1024px and 768px
- [ ] 2.3 Adjust chart height and scroll container styles for smooth page scrolling

## 3. JavaScript Logic Updates

- [ ] 3.1 Update `app.js` to remove tab event listeners and `switchChartTab` function
- [ ] 3.2 Ensure `refreshDashboard()` renders both `renderDepthChart` and `updateCandlestickChart` on every polling update
- [ ] 3.3 Verify `candlestick.js` resize observer cleanly handles dynamic scaling

## 4. Verification

- [ ] 4.1 Run `uv run pytest tests/` to confirm all API and engine unit tests pass
- [ ] 4.2 Run `uv run prek run -v --show-diff-on-failure --all-files` code quality checks
