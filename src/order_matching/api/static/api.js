const API_BASE = window.location.origin;

/**
 * Place a new limit or market order.
 * @param {Object} orderPayload - The order details
 * @returns {Promise<Object>} API response
 */
export async function placeOrder(orderPayload) {
  const res = await fetch(`${API_BASE}/place`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ orders: [orderPayload] })
  });
  const data = await res.json();
  if (!res.ok) {
    let errMsg = 'Failed to place order';
    if (data.detail) {
      if (Array.isArray(data.detail)) {
        errMsg = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(' | ');
      } else {
        errMsg = data.detail;
      }
    }
    throw new Error(errMsg);
  }
  return data;
}

/**
 * Cancel an outstanding order by ID.
 * @param {string} orderId - The order ID to cancel
 * @returns {Promise<Object>} API response
 */
export async function cancelOrder(orderId) {
  const res = await fetch(`${API_BASE}/orders/${orderId}`, {
    method: 'DELETE'
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to cancel order');
  }
  return data;
}

/**
 * Trigger order matching run.
 * @param {string} timestampStr - Timestamp for matching
 * @returns {Promise<Object>} API response
 */
export async function matchOrders(timestampStr) {
  const res = await fetch(`${API_BASE}/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ timestamp: timestampStr })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to execute matching');
  }
  return data;
}

/**
 * Reset the matching engine.
 * @param {number|null} seed - Seed for random generator
 * @param {boolean} prepopulate - Prepopulate with mock orders
 * @returns {Promise<Object>} API response
 */
export async function resetEngine(seed, prepopulate) {
  const res = await fetch(`${API_BASE}/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seed: seed, prepopulate: prepopulate })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to reset market state');
  }
  return data;
}

/**
 * Fetch current order book, trade history, and summary levels in parallel.
 * @returns {Promise<Object>} Object containing orders, trades, and summary data
 */
export async function fetchMarketState() {
  const [ordersRes, tradesRes, summaryRes] = await Promise.all([
    fetch(`${API_BASE}/orders`),
    fetch(`${API_BASE}/trades`),
    fetch(`${API_BASE}/summary`)
  ]);

  if (!ordersRes.ok || !tradesRes.ok || !summaryRes.ok) {
    throw new Error('Failed to fetch market state from server');
  }

  const orderBookData = await ordersRes.json();
  const tradeData = (await tradesRes.json()).trades;
  const summaryData = await summaryRes.json();

  return { orderBookData, tradeData, summaryData };
}
