# Order Book Matching Engine

![pytest](https://github.com/khrapovs/OrderBookMatchingEngine/actions/workflows/workflow.yaml/badge.svg)
[![!pypi](https://img.shields.io/pypi/v/order-matching)](https://pypi.org/project/order-matching/)
[![!python-versions](https://img.shields.io/pypi/pyversions/order-matching)](https://pypi.org/project/order-matching/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview

This package is a simple order book matching engine implementation in Python. Its main features are:

- price-time priority
- limit and market orders
- order cancellation and expiration
- conversion into polars LazyFrame of orders, executed trades, order book summary (optional polars dependency)

## Install

```shell
# Core matching engine only
pip install order-matching

# With polars export support (recommended for data science workflows)
pip install order-matching[polars]
```

## Documentation

[khrapovs.github.io/OrderBookMatchingEngine](https://khrapovs.github.io/OrderBookMatchingEngine/)

## Usage

```python
>>> from datetime import datetime, timedelta
>>> from pprint import pp
>>> import polars as pl

>>> from order_matching.matching_engine import MatchingEngine
>>> from order_matching.order import LimitOrder
>>> from order_matching.side import Side
>>> from order_matching.orders import Orders

>>> matching_engine = MatchingEngine(seed=123)
>>> timestamp = datetime(2023, 1, 1)
>>> transaction_timestamp = timestamp + timedelta(days=1)
>>> buy_order = LimitOrder(side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="a", trader_id="x")
>>> sell_order = LimitOrder(side=Side.SELL, price=0.8, size=1.6, timestamp=timestamp, order_id="b", trader_id="y")
>>> executed_trades = matching_engine.match(orders=Orders([buy_order, sell_order]), timestamp=transaction_timestamp)

>>> pp(executed_trades.trades)
[Trade(side=SELL,
       price=1.2,
       size=1.6,
       incoming_order_id='b',
       book_order_id='a',
       execution=LIMIT,
       trade_id='c4da537c-1651-4dae-8486-7db30d67b366',
       timestamp=datetime.datetime(2023, 1, 2, 0, 0))]


```

### Data Export (Polars)

If you installed with `[polars]` extra, you can export data to polars LazyFrame:

```python
>>> from order_matching.matching_engine import MatchingEngine
>>> from order_matching.exporters.polars import PolarsExporter
>>> from order_matching.orders import Orders
>>> from order_matching.executed_trades import ExecutedTrades

>>> matching_engine = MatchingEngine(seed=123)
>>> exporter = PolarsExporter()
>>> orders_df = exporter.export_orders(Orders())
>>> trades_df = exporter.export_trades(ExecutedTrades())

>>> # Legacy API (deprecated, will be removed in 1.0.0)
>>> trades_df = ExecutedTrades().to_frame()

```

## Related Projects

- [bmoscon/orderbook](https://github.com/bmoscon/orderbook)
- [Kautenja/limit-order-book](https://github.com/Kautenja/limit-order-book)

## Contribute

Install project in editable mode and sync all dependencies:

```shell
uv sync --all-groups --all-extras
```

and use pre-commit to make sure that your code is formatted and linted automatically:

```shell
uv run prek install
```

Run tests:

```shell
uv run pytest
```

Run benchmark and see the result either in the terminal or as a plot in `benchmark_history.svg`:

```shell
./benchmark.sh
```

Build and serve documentation website:

```shell
uv run mkdocs serve
```
