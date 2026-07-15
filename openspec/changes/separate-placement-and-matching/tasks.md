## 1. Core Logic Implementation

- [ ] 1.1 Add `place` method to `MatchingEngine` class to append orders to the book and queue them for matching.
- [ ] 1.2 Modify `match` method in `MatchingEngine` to temporarily remove any existing non-cancelled order from `unprocessed_orders` during processing.

## 2. API Endpoints Alignment

- [ ] 2.1 Refactor the `POST /orders` router in `place_orders.py` to invoke `engine.place` and remove matching logic, trade accumulation, and trades from response.

## 3. Test Alignment and Verification

- [ ] 3.1 Update `tests/test_api/test_place_orders.py` to expect orders to be placed without trades being executed.
- [ ] 3.2 Update `tests/test_api/test_match.py` to explicitly trigger `/match` in scenarios testing crossing orders.
- [ ] 3.3 Update `tests/test_api/test_workflows.py` to explicitly call `/match` after placing crossing orders.
- [ ] 3.4 Run all tests using pytest to verify complete correctness of the implementation.
