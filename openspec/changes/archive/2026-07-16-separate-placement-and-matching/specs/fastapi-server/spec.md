## MODIFIED Requirements

### Requirement: Place Orders

The system SHALL accept one or more orders via HTTP POST and add them to the order book without triggering matching.

#### Scenario: Place single limit order successfully
- **WHEN** client sends POST /orders with valid limit order
- **THEN** system returns 200 with confirmation and order details

#### Scenario: Place batch of orders successfully
- **WHEN** client sends POST /orders with multiple valid orders
- **THEN** system returns 200 with confirmation for all orders

#### Scenario: Place market order successfully
- **WHEN** client sends POST /orders with valid market order (no price)
- **THEN** system returns 200 with confirmation and order details

#### Scenario: Reject order with duplicate ID
- **WHEN** client sends order with ID that already exists in order book
- **THEN** system returns 400 with error message indicating duplicate ID

#### Scenario: Reject order with invalid data
- **WHEN** client sends order with missing required fields or invalid values
- **THEN** system returns 422 with validation errors

#### Scenario: Reject order with negative size
- **WHEN** client sends order with size ≤ 0
- **THEN** system returns 422 with validation error
