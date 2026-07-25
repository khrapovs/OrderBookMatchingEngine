## Why

The interactive dashboard UI currently displays the title and subtitle ("High-Performance Matching Simulator") but lacks visibility into the installed package version of the order matching engine. Displaying the version next to the subtitle provides users and developers immediate clarity on which build/release of `order-matching` is running.

## What Changes

- **Backend**:
  - Add `VersionResponse` Pydantic model (`version: str`) to `src/order_matching/api/models/responses.py`.
  - Add `GET /version` endpoint in `src/order_matching/api/routes/version.py` returning `VersionResponse(version=__version__)`.
  - Include `version.py` router in `src/order_matching/api/routes/__init__.py`.
  - Add API unit tests for `GET /version`.

- **Frontend**:
  - Add `#version-badge` element next to the subtitle in `src/order_matching/api/static/index.html`.
  - Style `.version-badge` in `src/order_matching/api/static/styles.css` as a subtle tech badge using monospace font.
  - Add `fetchVersion()` helper in `src/order_matching/api/static/api.js` and call it on page initialization in `ui.js`/`app.js` to dynamically populate the badge.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `fastapi-server`: Add `GET /version` endpoint requirement returning package version typed with `VersionResponse`.
- `frontend-ui`: Add requirement to render the version as a tech badge next to the subtitle in the header.

## Impact

- Affected files:
  - `src/order_matching/api/models/responses.py`
  - `src/order_matching/api/routes/version.py` (new)
  - `src/order_matching/api/routes/__init__.py`
  - `src/order_matching/api/static/index.html`
  - `src/order_matching/api/static/styles.css`
  - `src/order_matching/api/static/api.js`
  - `src/order_matching/api/static/ui.js` or `app.js`
  - `tests/test_api/test_version.py` (new)
- No breaking changes to existing endpoints or data structures.
