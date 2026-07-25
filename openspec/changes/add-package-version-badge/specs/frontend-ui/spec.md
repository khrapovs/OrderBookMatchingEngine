## ADDED Requirements

### Requirement: Package Version Badge

The dashboard UI SHALL display the package version of the order book matching engine in the header next to the subtitle.

#### Scenario: Version badge rendered on page load
- **WHEN** user loads the web dashboard
- **THEN** the dashboard fetches GET /version and displays the package version in a styled tech badge next to the subtitle "High-Performance Matching Simulator"
