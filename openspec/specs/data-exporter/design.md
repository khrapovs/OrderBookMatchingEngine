# Exporter Architecture Design

**Date:** 2026-07-06
**Status:** Approved
**Version:** 0.5.0

## Overview

This design document describes the refactoring of data export functionality in the order-matching engine to separate domain logic from format-specific export logic. The current implementation embeds polars export methods (`to_frame()`) directly in domain classes (`Orders`, `ExecutedTrades`), creating tight coupling and preventing extensibility to other export formats.

## Goals

1. **Separation of Concerns:** Remove export logic from domain models so they remain focused on business logic
2. **Extensibility:** Enable support for multiple export formats (JSON, CSV, Arrow, databases) without modifying domain classes
3. **Optional Dependencies:** Make polars an optional dependency so the core matching engine has minimal requirements
4. **Backward Compatibility:** Maintain existing `to_frame()` API during a deprecation period
5. **Type Safety:** Use generics to ensure type-safe export implementations

## Non-Goals

- Changing the matching engine's core algorithms or data structures
- Modifying the pandera schema definitions (they remain unchanged)
- Adding new export formats in this phase (architecture only; implementations come later)
- Performance optimization of export operations

## Current State

### Problems

1. **Tight Coupling:** `Orders` and `ExecutedTrades` classes import polars and pandera, making them dependent on data science libraries
2. **Single Format:** Only polars LazyFrame export is supported; adding CSV/JSON requires modifying domain classes
3. **Mandatory Dependencies:** Users who only need the matching engine must install polars/pandera
4. **Responsibility Violation:** Domain classes handle both business logic (order management) and presentation logic (data formatting)

### Current Implementation

```python
# orders.py
import polars as pl
from pandera.typing.polars import LazyFrame

class Orders:
    def to_frame(self) -> LazyFrame[OrderDataSchema]:
        # 15 lines of polars-specific conversion logic
        if len(self.orders) == 0:
            return OrderDataSchema.empty().lazy()
        data = [asdict(order) for order in self.orders]
        # enum to string conversions...
        return pl.LazyFrame(data)
```

Similar logic exists in `ExecutedTrades.to_frame()`.

## Proposed Architecture

### Module Structure

```
src/order_matching/
├── exporters/
│   ├── __init__.py          # Exports Exporter, PolarsExporter
│   ├── base.py              # Abstract base class
│   └── polars.py            # Polars implementation
├── orders.py                # Modified: thin wrapper method
├── executed_trades.py       # Modified: thin wrapper method
└── schemas.py               # Unchanged
```

Future exporters can be added as new files in the `exporters/` directory without touching existing code.

### Abstract Interface

**File:** `exporters/base.py`

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class Exporter(ABC, Generic[T]):
    """Abstract base class for data exporters.

    Type parameter T represents the output format type
    (e.g., LazyFrame, dict, str for JSON/CSV).
    """

    @abstractmethod
    def export_orders(self, orders: Orders) -> T:
        """Convert Orders collection to target format.

        Parameters
        ----------
        orders : Orders
            Orders collection to export

        Returns
        -------
        T
            Exported data in target format
        """
        pass

    @abstractmethod
    def export_trades(self, trades: ExecutedTrades) -> T:
        """Convert ExecutedTrades collection to target format.

        Parameters
        ----------
        trades : ExecutedTrades
            Trades collection to export

        Returns
        -------
        T
            Exported data in target format
        """
        pass
```

**Design Decisions:**

- **ABC over Protocol:** Using ABC ensures all exporters explicitly implement required methods
- **Generic Type Variable:** `T` provides compile-time type safety for return values
- **Stateless Methods:** Exporters are pure transformers with no internal state
- **Explicit Method Names:** `export_orders` and `export_trades` (not overloaded `export`) for clarity

### Polars Implementation

**File:** `exporters/polars.py`

```python
from dataclasses import asdict
from typing import cast

import polars as pl
from pandera.typing.polars import LazyFrame

from order_matching.exporters.base import Exporter
from order_matching.schemas import OrderDataSchema, TradeDataSchema
from order_matching.orders import Orders
from order_matching.executed_trades import ExecutedTrades


class PolarsExporter(Exporter[LazyFrame]):
    """Export collections to polars LazyFrame format."""

    def export_orders(self, orders: Orders) -> LazyFrame[OrderDataSchema]:
        """Export Orders to validated polars LazyFrame."""
        if len(orders) == 0:
            return cast(LazyFrame[OrderDataSchema], OrderDataSchema.empty().lazy())

        data = [asdict(order) for order in orders]
        for d in data:
            d[OrderDataSchema.side] = d[OrderDataSchema.side].name
            d[OrderDataSchema.execution] = d[OrderDataSchema.execution].name
            d[OrderDataSchema.status] = d[OrderDataSchema.status].name
        return cast(LazyFrame[OrderDataSchema], pl.LazyFrame(data))

    def export_trades(self, trades: ExecutedTrades) -> LazyFrame[TradeDataSchema]:
        """Export ExecutedTrades to validated polars LazyFrame."""
        trade_list = trades.trades
        if len(trade_list) == 0:
            return cast(LazyFrame[TradeDataSchema], TradeDataSchema.empty().lazy())

        data = [asdict(trade) for trade in trade_list]
        for d in data:
            d[TradeDataSchema.side] = d[TradeDataSchema.side].name
            d[TradeDataSchema.execution] = d[TradeDataSchema.execution].name
        return cast(LazyFrame[TradeDataSchema], pl.LazyFrame(data))
```

**Implementation Notes:**

- Logic is extracted verbatim from existing `to_frame()` methods
- Enum-to-string conversion remains in polars exporter (format-specific concern)
- Empty collection handling preserved
- Pandera schema validation still applies

### Backward Compatibility

The existing `to_frame()` methods will remain but delegate to exporters:

**File:** `orders.py` (modified)

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandera.typing.polars import LazyFrame
    from order_matching.schemas import OrderDataSchema

class Orders:
    # ... existing methods unchanged ...

    def to_frame(self) -> LazyFrame[OrderDataSchema]:
        """Get polars LazyFrame with all orders in the storage.

        .. deprecated:: 0.5.0
            Use ``PolarsExporter().export_orders(orders)`` instead.
            This method will be removed in version 1.0.0.

        Returns
        -------
        LazyFrame[OrderDataSchema]
        """
        from order_matching.exporters.polars import PolarsExporter
        return PolarsExporter().export_orders(self)
```

**File:** `executed_trades.py` (modified)

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandera.typing.polars import LazyFrame
    from order_matching.schemas import TradeDataSchema

class ExecutedTrades:
    # ... existing methods unchanged ...

    def to_frame(self) -> LazyFrame[TradeDataSchema]:
        """Get polars DataFrame of all stored trades.

        .. deprecated:: 0.5.0
            Use ``PolarsExporter().export_trades(trades)`` instead.
            This method will be removed in version 1.0.0.

        Returns
        -------
        LazyFrame[TradeDataSchema]
        """
        from order_matching.exporters.polars import PolarsExporter
        return PolarsExporter().export_trades(self)
```

**Strategy:**

- `TYPE_CHECKING` blocks prevent runtime imports of polars/pandera in core classes
- Lazy import of `PolarsExporter` inside method keeps polars optional
- Deprecation notices guide users to new API
- Deprecation timeline: deprecate in 0.5.0, remove in 1.0.0

**Migration Path:**

```python
# Old API (still works but deprecated)
orders.to_frame()

# New API (recommended)
from order_matching.exporters.polars import PolarsExporter
exporter = PolarsExporter()
exporter.export_orders(orders)
```

### Dependency Management

**File:** `pyproject.toml` (modified)

```toml
[project]
name = "order-matching"
dependencies = [
    # Core dependencies only - NO polars or pandera
]

[project.optional-dependencies]
polars = [
    "polars>=1.0.0",
    "pandera[polars]>=0.20.0",
]
all = [
    "order-matching[polars]",
]
```

**Installation Options:**

```bash
# Core engine only (no export capabilities)
pip install order-matching

# With polars export support
pip install order-matching[polars]

# With all export formats (future)
pip install order-matching[all]
```

**Import Behavior:**

- Core modules never import polars directly at module level
- `exporters/polars.py` imports polars normally (fails if not installed)
- Users calling `PolarsExporter` without `[polars]` get clear `ModuleNotFoundError`
- Old `to_frame()` methods work seamlessly if polars is installed

### Future Extensibility

The architecture enables adding new exporters without modifying existing code:

```python
# Future: exporters/json.py
class JSONExporter(Exporter[str]):
    def export_orders(self, orders: Orders) -> str:
        # JSON serialization logic
        pass

    def export_trades(self, trades: ExecutedTrades) -> str:
        # JSON serialization logic
        pass

# Future: exporters/csv.py
class CSVExporter(Exporter[str]):
    def export_orders(self, orders: Orders) -> str:
        # CSV formatting logic
        pass

# Future: exporters/arrow.py
class ArrowExporter(Exporter[pa.Table]):
    def export_orders(self, orders: Orders) -> pa.Table:
        # Arrow table conversion
        pass
```

Each exporter:
- Lives in its own file
- Has its own optional dependency group
- Follows the same `Exporter[T]` contract
- Requires zero changes to domain classes

## Testing Strategy

### New Tests

**File:** `tests/test_exporters/test_polars_exporter.py`

```python
import pytest
from order_matching.exporters.polars import PolarsExporter
from order_matching.schemas import OrderDataSchema, TradeDataSchema
from order_matching.orders import Orders
from order_matching.executed_trades import ExecutedTrades

class TestPolarsExporter:
    def test_export_empty_orders(self):
        """Test exporting empty Orders collection."""
        exporter = PolarsExporter()
        orders = Orders()
        result = exporter.export_orders(orders)
        assert result.collect().equals(OrderDataSchema.empty())

    def test_export_orders_with_data(self, sample_orders):
        """Test exporting Orders with data."""
        exporter = PolarsExporter()
        result = exporter.export_orders(sample_orders)
        OrderDataSchema.validate(result, lazy=True)

    def test_export_empty_trades(self):
        """Test exporting empty ExecutedTrades."""
        exporter = PolarsExporter()
        trades = ExecutedTrades()
        result = exporter.export_trades(trades)
        assert result.collect().equals(TradeDataSchema.empty())

    def test_export_trades_with_data(self, sample_trades):
        """Test exporting ExecutedTrades with data."""
        exporter = PolarsExporter()
        result = exporter.export_trades(sample_trades)
        TradeDataSchema.validate(result, lazy=True)

    def test_enum_conversion(self, sample_orders):
        """Verify enums are converted to string names."""
        exporter = PolarsExporter()
        result = exporter.export_orders(sample_orders).collect()
        # All side/execution/status columns should be strings
        assert result['side'].dtype == pl.Utf8
```

### Existing Tests

Existing tests in `test_orders.py` and `test_executed_trades.py` for `to_frame()` methods remain unchanged. They verify backward compatibility by ensuring the old API still works.

### Test Coverage

- New exporter tests verify core export logic correctness
- Existing domain class tests verify backward compatibility
- Both test suites pass with identical expectations
- Future exporters follow the same test pattern

## Migration Guide

### For Library Maintainers

**Phase 1: Version 0.5.0 (this release)**
1. Add `exporters/` module with new architecture
2. Modify `orders.py` and `executed_trades.py` to delegate to exporters
3. Add deprecation warnings to `to_frame()` docstrings
4. Update README to show both old and new APIs
5. Make polars an optional dependency

**Phase 2: Version 0.6.0 - 0.9.x (transition period)**
- Maintain both APIs
- Update examples and documentation to prefer new API
- Monitor deprecation usage

**Phase 3: Version 1.0.0 (breaking change)**
- Remove `to_frame()` methods from domain classes
- Update README to only show new API
- Polars remains optional

### For Library Users

**Immediate (Version 0.5.0+):**

No action required. Existing code continues to work unchanged:

```python
# Still works, no changes needed
orders.to_frame()
trades.to_frame()
```

**Recommended (Version 0.5.0+):**

Migrate to new API to avoid future breakage:

```python
# Old
orders_df = orders.to_frame()
trades_df = trades.to_frame()

# New
from order_matching.exporters.polars import PolarsExporter

exporter = PolarsExporter()
orders_df = exporter.export_orders(orders)
trades_df = exporter.export_trades(trades)
```

**Installation:**

```bash
# If using polars export, add [polars] extra
pip install order-matching[polars]
```

## Trade-offs

### Advantages

✅ **Clean Separation:** Domain models have no knowledge of export formats
✅ **Extensible:** New formats don't require changes to core code
✅ **Optional Dependencies:** Core engine has minimal requirements
✅ **Type Safe:** Generic types ensure compile-time correctness
✅ **Backward Compatible:** Existing code continues working during deprecation period
✅ **Future-Proof:** Architecture supports JSON, CSV, databases, etc.

### Disadvantages

⚠️ **Slightly More Verbose:** Users must import and instantiate exporters
⚠️ **Breaking Change in 1.0:** Old API will eventually be removed
⚠️ **More Files:** Architecture spreads code across more modules

### Rejected Alternatives

**Approach 1: Simple Converter Module**
- Rejected in favor of Approach 2 for better extensibility
- Protocol-based approach provides clearer contracts and better type safety

**Approach 3: Mixin Pattern**
- Rejected because it doesn't fully separate responsibilities
- Still couples domain models to export logic through inheritance

## Success Criteria

1. **Functionality:** All existing tests pass without modification
2. **Backward Compatibility:** Old `to_frame()` API works identically to before
3. **Type Safety:** `mypy --strict` passes on all new code
4. **Optional Dependencies:** Core package installs without polars/pandera
5. **Documentation:** README clearly explains both APIs and migration path
6. **Extensibility:** Adding a JSON exporter requires only one new file

## Implementation Checklist

- [ ] Create `src/order_matching/exporters/` directory
- [ ] Implement `exporters/base.py` with abstract `Exporter` class
- [ ] Implement `exporters/polars.py` with `PolarsExporter`
- [ ] Implement `exporters/__init__.py` to export public interfaces
- [ ] Modify `orders.py` to delegate `to_frame()` to exporter
- [ ] Modify `executed_trades.py` to delegate `to_frame()` to exporter
- [ ] Update `pyproject.toml` to make polars optional
- [ ] Create test suite in `tests/test_exporters/test_polars_exporter.py`
- [ ] Verify all existing tests still pass
- [ ] Update README with new API examples
- [ ] Update documentation with deprecation timeline
- [ ] Add type checking validation for new code

## Open Questions

None. All design questions have been resolved during brainstorming.

## References

- Current implementation: `src/order_matching/orders.py:58-73`
- Current implementation: `src/order_matching/executed_trades.py:60-76`
- Schemas: `src/order_matching/schemas.py`
- Existing tests: `tests/test_orders.py:61-66`, `tests/test_executed_trades.py:53-61`
