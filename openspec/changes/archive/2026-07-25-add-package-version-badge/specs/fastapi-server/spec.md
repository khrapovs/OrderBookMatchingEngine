## ADDED Requirements

### Requirement: Get Package Version

The system SHALL return the installed package version of the order book matching engine.

#### Scenario: Get package version successfully
- **WHEN** client sends GET /version
- **THEN** system returns 200 OK with `VersionResponse` containing `version` string matching package `__version__`
