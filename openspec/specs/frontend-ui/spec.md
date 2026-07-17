# Spec: Frontend MVP for Order Book Matching Engine

## Objective
Implement a beautiful, responsive, and interactive single-page application (SPA) frontend for the order book matching engine. The UI will run directly in the browser and interface with the local FastAPI endpoints.

The primary user is a developer or trader testing the matching engine. Success looks like an intuitive dashboard that renders the state of the market in real-time, allowing users to interact with orders and see the resulting matching behavior.

## Core Features
1. **Add Order Form**: Easily submit Limit or Market orders (BUY/SELL) with client-side default/auto-generation of timestamps and order IDs.
2. **Cancel Order**: Click to cancel any outstanding order from the list.
3. **Trigger Matching**: One-click manual matching with customizable timestamp.
4. **Reset Market**: Clear all state in the matching engine (with optional seed input).
5. **Order Book Visualization**: A side-by-side bid-ask volume histogram/depth chart built using native SVG.
6. **Market Lists**: Clean, filterable lists of Outstanding Orders and Recent Trades.
7. **Auto-refresh**: Polling of market state every 1 second to keep the dashboard current.

## Tech Stack
- **Frontend Core**: HTML5, Vanilla JavaScript (ES6+), and CSS3.
- **Styling**: Vanilla CSS with a modern dark-mode financial dashboard design (using CSS variables, CSS grid/flexbox, custom animations). No TailwindCSS.
- **Backend Host**: Served directly by the existing FastAPI server from a static files directory (`src/order_matching/api/static`).
- **Dependencies**: No external javascript frameworks or plotting libraries (pure SVG charts and standard fetch API).

## Commands
- **Install dependencies (backend)**:
  ```shell
  uv sync --all-groups --all-extras
  ```
- **Start FastAPI server (with reload for development)**:
  ```shell
  uv run uvicorn order_matching.api.app:app --reload --port 8000
  ```
- **Run validation tools before commit**:
  ```shell
  uv run prek run -v --show-diff-on-failure --all-files
  ```

## Project Structure
We will add static files to the API package to keep execution simple and self-contained:
```
src/order_matching/api/
├── static/
│   ├── index.html   ← Main entry point and layout
│   ├── styles.css   ← Custom premium dashboard CSS styling
│   └── app.js       ← UI logic, data fetching, SVG visualization, and state management
```
And we will modify `src/order_matching/api/app.py` to mount the static files and redirect the root (or serve) the SPA interface.

## Code Style
- **JavaScript**: Use semantic ES6 features, clean helper functions for network requests, async/await, and native DOM API.
- **CSS**: Modern CSS with unified color system (CSS variables), grid systems, clear responsiveness, and interactive transitions.
- **HTML**: Clean semantic HTML5.

### Styling System (CSS Variables Example)
```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f8fafc;
  --text-muted: #94a3b8;
  --color-buy: #10b981;      /* Emerald Green */
  --color-buy-bg: rgba(16, 185, 129, 0.15);
  --color-sell: #ef4444;     /* Rose Red */
  --color-sell-bg: rgba(239, 68, 68, 0.15);
  --color-accent: #3b82f6;   /* Royal Blue */
  --font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
```

## Testing Strategy
- **Manual Verification**: Verify in Chrome/Safari/Firefox that orders can be placed, cancelled, and matched, and that the depth chart updates correctly.
- **Browser Logs**: Ensure zero console errors or warnings.
- **Mock Verification**: Run the backend and perform end-to-end user actions (placing cross orders, matching, resetting) while observing frontend updates.

## Boundaries
- **Always**:
  - Keep python backend changes isolated to `app.py` and routes if needed to support the static mount.
  - Follow the python formatters/linters by running `prek`.
- **Ask First**:
  - Adding external Javascript packages (like chart libraries).
- **Never**:
  - Break existing Swagger documentation (`/docs`).
  - Modify core matching engine logic.

## Success Criteria
- [ ] UI is accessible at `http://localhost:8000/` or `http://localhost:8000/ui`.
- [ ] Bids and Asks are rendered as an SVG histogram showing cumulative size at each price level.
- [ ] Forms validate input fields and show clear error messages if placement fails (e.g. 400 or 422 errors).
- [ ] Recent trades and outstanding orders are listed, with trade side highlighted (Green for Buy, Red for Sell).
- [ ] Outstanding orders show an active "Cancel" button that successfully deletes the order.
- [ ] Manual matching works, sending the matching timestamp correctly.
- [ ] Reset button successfully clears all order book and trade data.
- [ ] Polling functions properly without memory leaks.

## Open Questions / Assumptions
1. **Root path route**: Should we mount the SPA directly at the root `/` and move Swagger to `/docs`? (Currently `/` redirects to `/docs`).
2. **Trader IDs**: Since placement requires `trader_id`, should we pre-populate the form with a random or selected trader ID?
