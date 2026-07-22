const API_BASE = window.location.origin;

/**
 * Helper to perform HTTP fetch requests and extract JSON/errors uniformly.
 */
async function request(path, options = {}, defaultErrorMsg = 'Request failed') {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, options);
  const data = await res.json();

  if (!res.ok) {
    let errMsg = defaultErrorMsg;
    if (data && data.detail) {
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
 * Place a new limit or market order.
 * @param {Object} orderPayload - The order details
 * @returns {Promise<Object>} API response
 */
export async function placeOrder(orderPayload) {
  return request('/place', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ orders: [orderPayload] })
  }, 'Failed to place order');
}

/**
 * Cancel an outstanding order by ID.
 * @param {string} orderId - The order ID to cancel
 * @returns {Promise<Object>} API response
 */
export async function cancelOrder(orderId) {
  return request(`/orders/${orderId}`, {
    method: 'DELETE'
  }, 'Failed to cancel order');
}

/**
 * Trigger order matching run.
 * @param {string} timestampStr - Timestamp for matching
 * @returns {Promise<Object>} API response
 */
export async function matchOrders(timestampStr) {
  return request('/match', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ timestamp: timestampStr })
  }, 'Failed to execute matching');
}

/**
 * Reset the matching engine.
 * @param {number|null} seed - Seed for random generator
 * @returns {Promise<Object>} API response
 */
export async function resetEngine(seed) {
  return request('/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seed: seed })
  }, 'Failed to reset market state');
}

/**
 * Fetch current order book, trade history, and summary levels in parallel.
 * @returns {Promise<Object>} Object containing orders, trades, and summary data
 */
export async function fetchMarketState() {
  const [orderBookData, tradesData, summaryData] = await Promise.all([
    request('/orders', {}, 'Failed to fetch orders'),
    request('/trades', {}, 'Failed to fetch trades'),
    request('/summary', {}, 'Failed to fetch summary')
  ]);

  return {
    orderBookData,
    tradeData: tradesData.trades,
    summaryData
  };
}
