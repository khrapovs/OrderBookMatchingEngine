# External Integrations

## Core Sections

### 1) Integration Inventory

| System | Type (API/DB/Queue/etc) | Purpose | Auth model | Criticality | Evidence |
|--------|---------------------------|---------|------------|-------------|----------|
| PyPI | Package registry | Publishing releases | Trusted publishing (OIDC) | High (for releases) | .github/workflows/workflow.yaml lines 111-137 |
| GitHub Actions | CI/CD platform | Automated testing, benchmarking, code quality, docs, publishing | GitHub token | High (for development workflow) | .github/workflows/workflow.yaml |

**Note**: This is a library package with no runtime external integrations (no databases, APIs, message queues, or external services called during execution).

### 2) Data Stores

| Store | Role | Access layer | Key risk | Evidence |
|-------|------|--------------|----------|----------|
| None | N/A | N/A | N/A | Library keeps all state in memory (OrderBook, ExecutedTrades) |

### 3) Secrets and Credentials Handling

- Credential sources: GitHub Actions trusted publishing (OIDC) for PyPI (no stored secrets)
- Hardcoding checks: No hardcoded credentials found (no API keys, tokens, or connection strings in source)
- Rotation or lifecycle notes: PyPI uses trusted publishing—no manual token management needed (.github/workflows/workflow.yaml line 119)

### 4) Reliability and Failure Behavior

- Retry/backoff behavior: None (no external calls in library runtime)
- Timeout policy: Not applicable (no network operations)
- Circuit-breaker or fallback behavior: Not applicable

### 5) Observability for Integrations

- Logging around external calls: Not applicable (no external calls in library)
- Metrics/tracing coverage: Not applicable (library delegates observability to consuming applications)
- Missing visibility gaps: None (library has no external integrations to observe)

### 6) Evidence

- .github/workflows/workflow.yaml (CI/CD and PyPI publishing)
- pyproject.toml (project URLs, no database or API dependencies)
- Source code inspection (no http, database, or queue client usage)

## Additional Notes

- **Development-time integrations only**: All integrations are development/CI-time (GitHub Actions, PyPI publishing), not runtime.
- **Optional polars dependency**: If installed, polars is used for data export, but this is a local computation dependency, not an external integration.
- **User responsibility**: Applications using this library are responsible for their own integrations (e.g., persisting orders/trades to a database, exposing via API, etc.)
