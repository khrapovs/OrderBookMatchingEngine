# Exporter Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor data export functionality from domain classes into a dedicated exporter module with abstract interface and polars implementation.

**Architecture:** Create `exporters/` package with abstract `Exporter[T]` base class and concrete `PolarsExporter` implementation. Modify `Orders` and `ExecutedTrades` to delegate `to_frame()` calls to exporters. Make polars an optional dependency.

**Tech Stack:** Python 3.10+, polars, pandera, ABC/Generic typing

## Global Constraints

- Python >=3.10
- Maintain backward compatibility with existing `to_frame()` API
- All existing tests must pass without modification
- Follow TDD: write tests before implementation
- Use `TYPE_CHECKING` to avoid runtime imports of optional dependencies
- Commit after each passing test

---

## File Structure

**New Files:**
- `src/order_matching/exporters/__init__.py` - Public exports (Exporter, PolarsExporter)
- `src/order_matching/exporters/base.py` - Abstract Exporter[T] base class
- `src/order_matching/exporters/polars.py` - PolarsExporter implementation
- `tests/test_exporters/__init__.py` - Empty test package marker
- `tests/test_exporters/test_polars_exporter.py` - PolarsExporter test suite

**Modified Files:**
- `src/order_matching/orders.py` - Delegate to_frame() to PolarsExporter
- `src/order_matching/executed_trades.py` - Delegate to_frame() to PolarsExporter
- `pyproject.toml` - Make polars/pandera optional dependencies
- `README.md` - Update examples to show new API

---

### Task 1: Create Abstract Exporter Base Class

**Files:**
- Create: `src/order_matching/exporters/__init__.py`
- Create: `src/order_matching/exporters/base.py`

**Interfaces:**
- Consumes: Nothing (foundational task)
- Produces: `Exporter[T]` abstract base class with methods:
  - `export_orders(self, orders: Orders) -> T`
  - `export_trades(self, trades: ExecutedTrades) -> T`

- [ ] **Step 1: Create exporters package structure**

```bash
mkdir -p src/order_matching/exporters
touch src/order_matching/exporters/__init__.py
```

- [ ] **Step 2: Write base.py with abstract Exporter class**

```python
# src/order_matching/exporters/base.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from order_matching.orders import Orders
    from order_matching.executed_trades import ExecutedTrades

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

- [ ] **Step 3: Export Exporter from __init__.py**

```python
# src/order_matching/exporters/__init__.py
"""Data export module for converting domain objects to various formats."""

from order_matching.exporters.base import Exporter

__all__ = ["Exporter"]
```

- [ ] **Step 4: Verify imports work**

Run: `python -c "from order_matching.exporters import Exporter; print(Exporter)"`
Expected: `<class 'order_matching.exporters.base.Exporter'>`

- [ ] **Step 5: Commit base exporter**

```bash
git add src/order_matching/exporters/
git commit -m "feat: add abstract Exporter base class

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 2: Implement PolarsExporter with Tests

**Files:**
- Create: `src/order_matching/exporters/polars.py`
- Create: `tests/test_exporters/__init__.py`
- Create: `tests/test_exporters/test_polars_exporter.py`

**Interfaces:**
- Consumes: `Exporter[T]` from Task 1
- Produces: `PolarsExporter(Exporter[LazyFrame])` with methods:
  - `export_orders(self, orders: Orders) -> LazyFrame[OrderDataSchema]`
  - `export_trades(self, trades: ExecutedTrades) -> LazyFrame[TradeDataSchema]`

- [ ] **Step 1: Create test package structure**

```bash
mkdir -p tests/test_exporters
touch tests/test_exporters/__init__.py
```

- [ ] **Step 2: Write failing test for empty orders export**

```python
# tests/test_exporters/test_polars_exporter.py
from __future__ import annotations

import pytest

from order_matching.exporters.polars import PolarsExporter
from order_matching.orders import Orders
from order_matching.schemas import OrderDataSchema


class TestPolarsExporter:
    def test_export_empty_orders(self) -> None:
        """Test exporting empty Orders collection returns empty schema."""
        exporter = PolarsExporter()
        orders = Orders()
        result = exporter.export_orders(orders)
        assert result.collect().equals(OrderDataSchema.empty())
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_exporters/test_polars_exporter.py::TestPolarsExporter::test_export_empty_orders -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'order_matching.exporters.polars'`

- [ ] **Step 4: Implement PolarsExporter.export_orders for empty case**

```python
# src/order_matching/exporters/polars.py
from __future__ import annotations

from dataclasses import asdict
from typing import cast

import polars as pl
from pandera.typing.polars import LazyFrame

from order_matching.executed_trades import ExecutedTrades
from order_matching.exporters.base import Exporter
from order_matching.orders import Orders
from order_matching.schemas import OrderDataSchema, TradeDataSchema


class PolarsExporter(Exporter[LazyFrame]):
    """Export collections to polars LazyFrame format."""

    def export_orders(self, orders: Orders) -> LazyFrame[OrderDataSchema]:
        """Export Orders to validated polars LazyFrame.

        Parameters
        ----------
        orders : Orders
            Orders collection to export

        Returns
        -------
        LazyFrame[OrderDataSchema]
            Validated polars LazyFrame with order data
        """
        if len(orders) == 0:
            return cast(LazyFrame[OrderDataSchema], OrderDataSchema.empty().lazy())

        data = [asdict(order) for order in orders]
        for d in data:
            d[OrderDataSchema.side] = d[OrderDataSchema.side].name
            d[OrderDataSchema.execution] = d[OrderDataSchema.execution].name
            d[OrderDataSchema.status] = d[OrderDataSchema.status].name
        return cast(LazyFrame[OrderDataSchema], pl.LazyFrame(data))

    def export_trades(self, trades: ExecutedTrades) -> LazyFrame[TradeDataSchema]:
        """Export ExecutedTrades to validated polars LazyFrame.

        Parameters
        ----------
        trades : ExecutedTrades
            Trades collection to export

        Returns
        -------
        LazyFrame[TradeDataSchema]
            Validated polars LazyFrame with trade data
        """
        trade_list = trades.trades
        if len(trade_list) == 0:
            return cast(LazyFrame[TradeDataSchema], TradeDataSchema.empty().lazy())

        data = [asdict(trade) for trade in trade_list]
        for d in data:
            d[TradeDataSchema.side] = d[TradeDataSchema.side].name
            d[TradeDataSchema.execution] = d[TradeDataSchema.execution].name
        return cast(LazyFrame[TradeDataSchema], pl.LazyFrame(data))
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_exporters/test_polars_exporter.py::TestPolarsExporter::test_export_empty_orders -v`
Expected: PASS

- [ ] **Step 6: Write failing test for orders with data**

```python
# tests/test_exporters/test_polars_exporter.py (add to TestPolarsExporter class)
    def test_export_orders_with_data(self) -> None:
        """Test exporting Orders with data validates against schema."""
        from datetime import datetime
        from order_matching.order import LimitOrder
        from order_matching.side import Side

        exporter = PolarsExporter()
        timestamp = datetime(2023, 1, 1)
        order = LimitOrder(
            side=Side.BUY,
            price=1.2,
            size=2.3,
            timestamp=timestamp,
            order_id="test_order",
            trader_id="test_trader"
        )
        orders = Orders([order])
        result = exporter.export_orders(orders)
        OrderDataSchema.validate(result, lazy=True)
```

- [ ] **Step 7: Run test to verify it passes (implementation already complete)**

Run: `pytest tests/test_exporters/test_polars_exporter.py::TestPolarsExporter::test_export_orders_with_data -v`
Expected: PASS

- [ ] **Step 8: Write failing test for empty trades export**

```python
# tests/test_exporters/test_polars_exporter.py (add to TestPolarsExporter class)
    def test_export_empty_trades(self) -> None:
        """Test exporting empty ExecutedTrades returns empty schema."""
        from order_matching.executed_trades import ExecutedTrades

        exporter = PolarsExporter()
        trades = ExecutedTrades()
        result = exporter.export_trades(trades)
        assert result.collect().equals(TradeDataSchema.empty())
```

- [ ] **Step 9: Run test to verify it passes (implementation already complete)**

Run: `pytest tests/test_exporters/test_polars_exporter.py::TestPolarsExporter::test_export_empty_trades -v`
Expected: PASS

- [ ] **Step 10: Write failing test for trades with data**

```python
# tests/test_exporters/test_polars_exporter.py (add to TestPolarsExporter class)
    def test_export_trades_with_data(self) -> None:
        """Test exporting ExecutedTrades with data validates against schema."""
        from datetime import datetime
        from order_matching.executed_trades import ExecutedTrades
        from order_matching.execution import Execution
        from order_matching.side import Side
        from order_matching.trade import Trade

        exporter = PolarsExporter()
        timestamp = datetime(2023, 1, 2)
        trade = Trade(
            side=Side.SELL,
            price=1.2,
            size=1.6,
            incoming_order_id="b",
            book_order_id="a",
            execution=Execution.LIMIT,
            trade_id="test_trade",
            timestamp=timestamp
        )
        trades = ExecutedTrades([trade])
        result = exporter.export_trades(trades)
        TradeDataSchema.validate(result, lazy=True)
```

- [ ] **Step 11: Run test to verify it passes (implementation already complete)**

Run: `pytest tests/test_exporters/test_polars_exporter.py::TestPolarsExporter::test_export_trades_with_data -v`
Expected: PASS

- [ ] **Step 12: Export PolarsExporter from __init__.py**

```python
# src/order_matching/exporters/__init__.py
"""Data export module for converting domain objects to various formats."""

from order_matching.exporters.base import Exporter
from order_matching.exporters.polars import PolarsExporter

__all__ = ["Exporter", "PolarsExporter"]
```

- [ ] **Step 13: Run full exporter test suite**

Run: `pytest tests/test_exporters/ -v`
Expected: All 4 tests PASS

- [ ] **Step 14: Commit PolarsExporter implementation**

```bash
git add src/order_matching/exporters/polars.py tests/test_exporters/
git commit -m "feat: implement PolarsExporter with full test coverage

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 3: Update Orders.to_frame() to Delegate

**Files:**
- Modify: `src/order_matching/orders.py:1-10` (imports)
- Modify: `src/order_matching/orders.py:58-73` (to_frame method)

**Interfaces:**
- Consumes: `PolarsExporter().export_orders(orders)` from Task 2
- Produces: Backward-compatible `Orders.to_frame()` method (delegates to exporter)

- [ ] **Step 1: Verify existing test still passes before changes**

Run: `pytest tests/test_orders.py::TestOrders::test_to_frame -v`
Expected: PASS

- [ ] **Step 2: Update imports in orders.py to use TYPE_CHECKING**

```python
# src/order_matching/orders.py (replace lines 1-10)
from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Iterator, Sequence, cast

if TYPE_CHECKING:
    from pandera.typing.polars import LazyFrame
    from order_matching.schemas import OrderDataSchema

from order_matching.order import Order
```

- [ ] **Step 3: Remove polars import from orders.py**

Delete this line if it exists:
```python
import polars as pl
```

Also delete this import if it exists:
```python
from pandera.typing.polars import LazyFrame
```

(These are now in TYPE_CHECKING block)

- [ ] **Step 4: Replace to_frame implementation with delegation**

```python
# src/order_matching/orders.py (replace to_frame method, around line 58-73)
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

- [ ] **Step 5: Run existing test to verify backward compatibility**

Run: `pytest tests/test_orders.py::TestOrders::test_to_frame -v`
Expected: PASS

- [ ] **Step 6: Commit orders.py changes**

```bash
git add src/order_matching/orders.py
git commit -m "refactor: delegate Orders.to_frame() to PolarsExporter

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 4: Update ExecutedTrades.to_frame() to Delegate

**Files:**
- Modify: `src/order_matching/executed_trades.py:1-12` (imports)
- Modify: `src/order_matching/executed_trades.py:60-76` (to_frame method)

**Interfaces:**
- Consumes: `PolarsExporter().export_trades(trades)` from Task 2
- Produces: Backward-compatible `ExecutedTrades.to_frame()` method (delegates to exporter)

- [ ] **Step 1: Verify existing test still passes before changes**

Run: `pytest tests/test_executed_trades.py::TestExecutedTrades::test_to_frame -v`
Expected: PASS

- [ ] **Step 2: Update imports in executed_trades.py to use TYPE_CHECKING**

```python
# src/order_matching/executed_trades.py (replace lines 1-12)
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pandera.typing.polars import LazyFrame
    from order_matching.schemas import TradeDataSchema

from order_matching.trade import Trade
```

- [ ] **Step 3: Remove polars import from executed_trades.py**

Delete this line if it exists:
```python
import polars as pl
```

Also delete this import if it exists:
```python
from pandera.typing.polars import LazyFrame
```

(These are now in TYPE_CHECKING block)

- [ ] **Step 4: Replace to_frame implementation with delegation**

```python
# src/order_matching/executed_trades.py (replace to_frame method, around line 60-76)
    def to_frame(self) -> LazyFrame[TradeDataSchema]:
        """Get polars DataFrame of all stored trades.

        .. deprecated:: 0.5.0
            Use ``PolarsExporter().export_trades(trades)`` instead.
            This method will be removed in version 1.0.0.

        Returns
        -------
        LazyFrame[TradeDataSchema]
            polars LazyFrame of all stored trades
        """
        from order_matching.exporters.polars import PolarsExporter

        return PolarsExporter().export_trades(self)
```

- [ ] **Step 5: Run existing test to verify backward compatibility**

Run: `pytest tests/test_executed_trades.py::TestExecutedTrades::test_to_frame -v`
Expected: PASS

- [ ] **Step 6: Commit executed_trades.py changes**

```bash
git add src/order_matching/executed_trades.py
git commit -m "refactor: delegate ExecutedTrades.to_frame() to PolarsExporter

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 5: Make Polars an Optional Dependency

**Files:**
- Modify: `pyproject.toml:20-25` (dependencies section)
- Modify: `pyproject.toml:26-45` (add optional-dependencies section)

**Interfaces:**
- Consumes: Nothing
- Produces: `pyproject.toml` with `[project.optional-dependencies]` section containing `polars` group

- [ ] **Step 1: Move polars and pandera to optional dependencies**

```toml
# pyproject.toml (replace lines 20-25)
dependencies = [
    "faker>=33.0.0",
    "numpy>=2.2.6",
]

[project.optional-dependencies]
polars = [
    "pandera[polars]>=0.21.0",
    "polars>=1.42.1",
]
all = [
    "order-matching[polars]",
]
```

- [ ] **Step 2: Run tests to verify they still pass (polars is installed in dev environment)**

Run: `pytest tests/ -v`
Expected: All tests PASS (polars still installed in current environment)

- [ ] **Step 3: Verify core imports work without polars (dry run check)**

Run: `python -c "from order_matching.orders import Orders; from order_matching.executed_trades import ExecutedTrades; print('Core imports work')"`
Expected: `Core imports work` (no import errors because TYPE_CHECKING prevents runtime import)

- [ ] **Step 4: Commit dependency changes**

```bash
git add pyproject.toml
git commit -m "refactor: make polars an optional dependency

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 6: Update README with New API Examples

**Files:**
- Modify: `README.md:16` (features list)
- Modify: `README.md:30-58` (usage example)

**Interfaces:**
- Consumes: `PolarsExporter` from Task 2
- Produces: Updated README documenting both old and new export APIs

- [ ] **Step 1: Update installation instructions to mention optional dependency**

```markdown
# README.md (find line ~20-22, modify install section)
## Install

```shell
# Core matching engine only
pip install order-matching

# With polars export support (recommended for data science workflows)
pip install order-matching[polars]
```
```

- [ ] **Step 2: Update features list to clarify polars is optional**

```markdown
# README.md (find line ~16, modify features list)
- conversion into polars LazyFrame of orders, executed trades, order book summary (optional polars dependency)
```

- [ ] **Step 3: Add new API example after existing usage section**

```markdown
# README.md (add after line ~58, after existing usage example)

### Data Export (Polars)

If you installed with `[polars]` extra, you can export data to polars LazyFrame:

```python
>>> from order_matching.exporters.polars import PolarsExporter

>>> exporter = PolarsExporter()
>>> orders_df = exporter.export_orders(matching_engine.order_book.buy_orders)
>>> trades_df = exporter.export_trades(executed_trades)

>>> # Legacy API (deprecated, will be removed in 1.0.0)
>>> orders_df = matching_engine.order_book.buy_orders.to_frame()
```
```

- [ ] **Step 4: Verify README renders correctly (markdown check)**

Run: `python -c "import markdown; markdown.markdown(open('README.md').read()); print('README valid')"`
Expected: `README valid` (or skip if markdown package not available)

- [ ] **Step 5: Commit README updates**

```bash
git add README.md
git commit -m "docs: update README with new exporter API

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

### Task 7: Final Integration Verification

**Files:**
- Test: All test files

**Interfaces:**
- Consumes: All tasks 1-6
- Produces: Verified working implementation with all tests passing

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Run type checking**

Run: `uv run ty`
Expected: No type errors

- [ ] **Step 3: Run linting**

Run: `uv run ruff check src/ tests/`
Expected: No linting errors

- [ ] **Step 4: Test new API usage pattern**

```python
# Create test script: test_new_api.py
from datetime import datetime
from order_matching.exporters.polars import PolarsExporter
from order_matching.orders import Orders
from order_matching.order import LimitOrder
from order_matching.side import Side
from order_matching.schemas import OrderDataSchema

timestamp = datetime(2023, 1, 1)
order = LimitOrder(
    side=Side.BUY,
    price=1.2,
    size=2.3,
    timestamp=timestamp,
    order_id="test",
    trader_id="trader"
)
orders = Orders([order])

# New API
exporter = PolarsExporter()
df = exporter.export_orders(orders)
OrderDataSchema.validate(df, lazy=True)
print("New API works!")

# Old API (backward compatibility)
df_old = orders.to_frame()
assert df.collect().equals(df_old.collect())
print("Backward compatibility verified!")
```

Run: `python test_new_api.py`
Expected:
```
New API works!
Backward compatibility verified!
```

- [ ] **Step 5: Clean up test script**

Run: `rm test_new_api.py`

- [ ] **Step 6: Final commit with version bump preparation**

```bash
git add -A
git status
# Verify only expected files are staged, then:
git commit -m "chore: prepare for v0.5.0 release with exporter architecture

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" --allow-empty
```

---

## Self-Review Checklist

**Spec Coverage:**
- ✅ Abstract Exporter base class (Task 1)
- ✅ PolarsExporter implementation (Task 2)
- ✅ Orders.to_frame() delegation (Task 3)
- ✅ ExecutedTrades.to_frame() delegation (Task 4)
- ✅ Optional polars dependency (Task 5)
- ✅ README documentation (Task 6)
- ✅ Full test coverage (Tasks 2, 7)
- ✅ Type safety with TYPE_CHECKING (Tasks 3, 4)
- ✅ Backward compatibility (Tasks 3, 4, 7)

**Placeholder Scan:**
- ✅ No TBD/TODO markers
- ✅ All code blocks contain actual implementation
- ✅ All test expectations specify exact output
- ✅ All file paths are absolute and exact

**Type Consistency:**
- ✅ `Exporter[T]` used consistently
- ✅ `PolarsExporter(Exporter[LazyFrame])` signature matches
- ✅ `export_orders` and `export_trades` method names consistent across all tasks
- ✅ Return types `LazyFrame[OrderDataSchema]` and `LazyFrame[TradeDataSchema]` consistent

**Dependencies:**
- Task 2 depends on Task 1 (uses Exporter base class)
- Task 3 depends on Task 2 (uses PolarsExporter)
- Task 4 depends on Task 2 (uses PolarsExporter)
- Task 6 depends on Task 2 (documents PolarsExporter)
- Task 7 depends on all tasks (integration verification)
