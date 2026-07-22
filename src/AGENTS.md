# Purpose

Contains the `order_matching` Python package implementing a high-performance order book matching engine with optional REST API and simulation capabilities.

# Ownership

This directory owns all production source code for the order-matching package.

# Local Contracts

- All Python code follows the privacy contract: expose only methods/attributes used by other classes; prefix all others with `_`
- Type hints required for all public methods per project standards
- Docstrings follow NumPy convention (configured in pyproject.toml)
- Maximum 1 positional argument per function (PLR0917)
- Line length: 120 characters

# Work Guidance

- Core matching engine logic lives in root-level modules (order_book.py, matching_engine.py, order.py, orders.py, executed_trades.py, trade.py)
- Enums and schemas provide shared types
- Separate submodules: api (REST), simulation (market sim), exporters (data export)
- Use `uv run` prefix for all Python commands
- Never access private attributes/methods from outside the class

# Verification

```shell
uv run prek run -v --show-diff-on-failure --all-files
```

# Child DOX Index

- `order_matching/AGENTS.md` - Core matching engine package and submodules
