## 1. Backend Pydantic Model & Route

- [ ] 1.1 Add `VersionResponse` model in `src/order_matching/api/models/responses.py`
- [ ] 1.2 Create `src/order_matching/api/routes/version.py` with `GET /version` endpoint typed with `-> VersionResponse`
- [ ] 1.3 Register `version.py` router in `src/order_matching/api/routes/__init__.py`
- [ ] 1.4 Add unit tests for `GET /version` in `tests/test_api/test_version.py`

## 2. Frontend Dashboard UI

- [ ] 2.1 Update `src/order_matching/api/static/index.html` to add `<span id="version-badge" class="version-badge"></span>` next to the subtitle
- [ ] 2.2 Add `.version-badge` styling in `src/order_matching/api/static/styles.css`
- [ ] 2.3 Add `fetchVersion()` in `src/order_matching/api/static/api.js`
- [ ] 2.4 Update `src/order_matching/api/static/ui.js` / `app.js` to fetch and display the version on initialization

## 3. Verification & DOX Check

- [ ] 3.1 Run unit tests with `uv run pytest tests/test_api/`
- [ ] 3.2 Run pre-commit checks with `uv run prek run -v --show-diff-on-failure --all-files`
- [ ] 3.3 Verify DOX updates in `src/order_matching/api/AGENTS.md` if necessary
