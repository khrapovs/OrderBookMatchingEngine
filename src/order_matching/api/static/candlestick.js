// Candlestick chart module for OHLC visualization using Lightweight Charts

// LightweightCharts is loaded via CDN in index.html
// Reference: https://unpkg.com/lightweight-charts@4.1.3/
/* global LightweightCharts */

// STATE
let chart = null;
let candlestickSeries = null;
let currentInterval = 5; // default 5 seconds

/**
 * Compute OHLC candles from trade data
 * @param {Array} trades - Array of trade objects with timestamp and price
 * @param {number} intervalSeconds - Time bucket interval in seconds
 * @returns {Array} Array of candle objects with time, open, high, low, close
 */
export function computeCandles(trades, intervalSeconds) {
  if (!trades || trades.length === 0) {
    return [];
  }

  // Group trades into time buckets
  const buckets = new Map();

  trades.forEach(trade => {
    const timestamp = new Date(trade.timestamp).getTime() / 1000; // Convert to seconds
    const bucketTime = Math.floor(timestamp / intervalSeconds) * intervalSeconds;

    if (!buckets.has(bucketTime)) {
      buckets.set(bucketTime, []);
    }
    buckets.get(bucketTime).push(trade.price);
  });

  // Compute OHLC for each bucket
  const candles = [];
  for (const [bucketTime, prices] of buckets) {
    if (prices.length > 0) {
      candles.push({
        time: bucketTime,
        open: prices[0],
        high: Math.max(...prices),
        low: Math.min(...prices),
        close: prices[prices.length - 1]
      });
    }
  }

  // Sort by time
  candles.sort((a, b) => a.time - b.time);
  return candles;
}

/**
 * Initialize the Lightweight Charts instance
 * @param {HTMLElement} container - Container element for the chart
 */
export function initCandlestickChart(container) {
  // Check if LightweightCharts is available (loaded via CDN)
  if (typeof LightweightCharts === 'undefined') {
    console.error('Lightweight Charts library not loaded. Ensure the CDN script is included in index.html');
    return;
  }

  // Create chart with dark theme
  chart = LightweightCharts.createChart(container, {
    width: container.clientWidth,
    height: 240,
    layout: {
      background: { color: 'transparent' },
      textColor: '#9ca3af',
    },
    grid: {
      vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
      horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
      vertLine: {
        color: 'rgba(255, 255, 255, 0.25)',
        labelBackgroundColor: '#6366f1',
      },
      horzLine: {
        color: 'rgba(255, 255, 255, 0.25)',
        labelBackgroundColor: '#6366f1',
      },
    },
    rightPriceScale: {
      borderColor: 'rgba(255, 255, 255, 0.06)',
    },
    timeScale: {
      borderColor: 'rgba(255, 255, 255, 0.06)',
      timeVisible: true,
      secondsVisible: true,
    },
  });

  // Add candlestick series
  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#f43f5e',
    borderUpColor: '#10b981',
    borderDownColor: '#f43f5e',
    wickUpColor: '#10b981',
    wickDownColor: '#f43f5e',
  });

  // Handle window resize
  const resizeObserver = new ResizeObserver(entries => {
    if (chart && entries.length > 0) {
      const { width } = entries[0].contentRect;
      chart.applyOptions({ width });
    }
  });
  resizeObserver.observe(container);
}

/**
 * Render candlestick chart with candle data
 * @param {Array} candles - Array of OHLC candle objects
 */
export function renderCandlestickChart(candles) {
  if (!candlestickSeries) {
    console.warn('Candlestick series not initialized');
    return;
  }

  // Update series with new data
  candlestickSeries.setData(candles);

  // Fit content to visible range
  if (candles.length > 0) {
    chart.timeScale().fitContent();
  }
}

/**
 * Setup interval selector button handlers
 */
export function setupIntervalSelector() {
  const buttons = document.querySelectorAll('.interval-btn');

  buttons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const interval = parseInt(e.target.dataset.interval);
      if (interval) {
        currentInterval = interval;

        // Update active state
        buttons.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');

        // Trigger refresh to recompute with new interval
        const event = new CustomEvent('intervalChanged', { detail: { interval } });
        window.dispatchEvent(event);
      }
    });
  });
}

/**
 * Get current interval setting
 * @returns {number} Current interval in seconds
 */
export function getCurrentInterval() {
  return currentInterval;
}
