# Order Book Matching Engine

![pytest](https://github.com/khrapovs/OrderBookMatchingEngine/actions/workflows/workflow.yaml/badge.svg)
[![!pypi](https://img.shields.io/pypi/v/order-matching)](https://pypi.org/project/order-matching/)
[![!python-versions](https://img.shields.io/pypi/pyversions/order-matching)](https://pypi.org/project/order-matching/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview

This repository provides a high-performance order book matching engine implemented in Python, complete with a RESTful API layer and a real-time interactive simulation dashboard. Its main features are:

- **Core Engine**: Price-time priority matching supporting limit/market orders, order cancellation, and expiration.
- **Market Simulation**: A discrete-time state-passing simulation framework featuring registered trading agents (such as Poisson-arrival `NoiseTrader` entities), an event-driven `NewsFeed`, and a read-only `MarketView` proxy wrapper.
- **REST API**: FastAPI server for remote order placement, manual or automated matching/simulation runs, and engine controls.
- **Web UI**: Modern glassmorphic SPA dashboard featuring an integrated live-updating market simulation, manual order entry/cancellation, trades list, interactive SVG depth chart, and real-time OHLC candlestick chart visualization.
- **Data Export**: Direct conversion of order books, trades, and summary states into Polars LazyFrames (optional dependency).

## Install

```shell
# Core matching engine only
pip install order-matching

# With polars export support (recommended for data science workflows)
pip install order-matching[polars]

# With REST API and Web UI simulation support
pip install order-matching[web]

# Install all optional dependencies (polars + web)
pip install order-matching[all]
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
>>> from order_matching.enums import Side
>>> from order_matching.orders import Orders

>>> matching_engine = MatchingEngine(seed=123)
>>> timestamp = datetime(2023, 1, 1)
>>> transaction_timestamp = timestamp + timedelta(days=1)
>>> buy_order = LimitOrder(side=Side.BUY, price=1.2, size=2.3, timestamp=timestamp, order_id="a", trader_id="x")
>>> sell_order = LimitOrder(side=Side.SELL, price=0.8, size=1.6, timestamp=timestamp, order_id="b", trader_id="y")
>>> # Place orders without matching:
>>> matching_engine.place(orders=Orders([buy_order, sell_order]))
>>> # Trigger matching at a specific timestamp:
>>> executed_trades = matching_engine.match(timestamp=transaction_timestamp)
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
>>> from order_matching.orders import Orders
>>> from order_matching.executed_trades import ExecutedTrades
>>> from order_matching.exporters.polars import PolarsExporter

>>> exporter = PolarsExporter()
>>> orders_df = exporter.export_orders(Orders())
>>> trades_df = exporter.export_trades(ExecutedTrades())

>>> trades_df = ExecutedTrades().to_frame()

```

## REST API & Frontend

For demo, education, and backtesting workflows, a RESTful API layer and simple UI frontend are provided.

### Running frontend and API server

Start the API server and frontend using the `fastapi` CLI:

```shell
uv run fastapi dev
```

Or run with `uvicorn`:

```shell
uv run uvicorn order_matching.api.app:app --reload
```

### Interactive Dashboard UI

The API server mounts a modern, glassmorphic dark-theme Single Page Application (SPA) dashboard available at the root URL: [http://127.0.0.1:8000](http://127.0.0.1:8000) (redirects to `/ui`).

Features include:
- **Live Market Simulation**: The dashboard runs an active market simulation with a pool of preconfigured automated traders placing orders organically at random intervals. Manual orders placed via the UI match and execute directly against these automated traders.
- **Engine Control & Pause/Resume**: The automated matching runs and the simulation steps run every second by default. They can be paused or resumed dynamically using the clickable **Engine Status** button in the header, freezing the simulated market state.
- **Order Placement & Cancellation**: Easily place new limit or market orders manually and cancel outstanding orders in real-time.
- **Depth Chart Visualization**: An interactive, responsive SVG cumulative depth chart with vertical cursor tracking and detailed hover tooltips.
- **Candlestick Chart Visualization**: Real-time OHLC (Open, High, Low, Close) candlestick chart powered by [Lightweight Charts](https://tradingview.github.io/lightweight-charts/) with configurable time intervals (5s, 15s, 30s, 1m), zoom, pan, and crosshair interactions for visualizing price evolution during simulation runs.
- **Real-Time Feeds**: Auto-refreshing logs of outstanding orders, recent trade ticks, current bid-ask spread, and top bid/ask levels.
- **Market Reset**: Modal controls to clear the entire market state and restart the simulation from scratch, with support for random seed specification.

### API Endpoints

Explore interactive API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

- `POST /place`: Place a batch of one or more orders without triggering matching.
- `POST /match`: Trigger matching at a specific timestamp for all queued/placed orders.
- `GET /orders`: Retrieve the current unmatched order book state (grouped by price).
- `GET /trades`: Retrieve trade execution history (with optional `from_timestamp` query filter).
- `DELETE /orders/{order_id}`: Cancel an active order by ID.
- `POST /reset`: Reset the engine state (with optional random `seed`).
- `GET /summary`: Retrieve aggregated order book price levels (matching `OrderBook.summary()`).

### API Limitations

- **Single-User / Educational Use**: The server uses in-memory state and is not thread-safe.
- **No Persistence**: Restarting the server clears all order book and trade history state.

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
