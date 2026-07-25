## Context

The order matching engine provides a FastAPI backend and a static HTML/JS frontend dashboard. The dashboard header presents the main application title and subtitle. To improve system transparency, the application needs to expose its installed package version dynamically via a dedicated REST API endpoint and present it visually as a tech badge in the header.

## Goals / Non-Goals

**Goals:**
- Provide a strongly-typed `GET /version` FastAPI endpoint returning `VersionResponse` (`{"version": "..."}`).
- Render a styled tech badge next to the subtitle in the web dashboard UI without causing layout shift.
- Ensure the endpoint and models adhere to project DOX contracts and FastAPI best practices (using `-> VersionResponse` return type annotation).

**Non-Goals:**
- Build system version bumps or automated git tag generation.
- Dynamic web socket or server-sent events for version changes.

## Decisions

### Decision 1: Dedicated `GET /version` API Endpoint vs Reusing `/openapi.json`
- **Choice**: Create `GET /version` in `src/order_matching/api/routes/version.py`.
- **Rationale**: An explicit endpoint is lightweight (~30 bytes payload vs ~10KB OpenAPI schema), cleanly documented in API models, and easily testable.
- **Alternatives Considered**: Fetching `/openapi.json` directly from JS. Rejected to avoid fetching full API schema overhead on page startup.

### Decision 2: Return Type Annotation (`-> VersionResponse`)
- **Choice**: Annotate the router handler with `def get_version() -> VersionResponse:` instead of `response_model=VersionResponse`.
- **Rationale**: Follows modern FastAPI best practices (FastAPI 0.89+ & Pydantic v2), allowing FastAPI to infer the OpenAPI schema and response validation directly while giving full IDE type hints.

### Decision 3: Visual Design & Frontend Integration
- **Choice**: Add `<span id="version-badge" class="version-badge"></span>` next to the subtitle.
- **Styling**: `JetBrains Mono` font, 0.725rem font size, rounded corners (`border-radius: 4px`), translucent dark background (`rgba(255, 255, 255, 0.08)`), and subtle border.

## Risks / Trade-offs

- **[Risk] Package version not found in uninstalled dev mode** → `src/order_matching/__init__.py` safely catches `PackageNotFoundError` and falls back gracefully.
- **[Risk] Layout shift while fetching version** → Badge element remains empty or hidden until populated by the async API call.
