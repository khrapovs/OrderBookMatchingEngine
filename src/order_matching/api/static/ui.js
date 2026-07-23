// Cache DOM elements
let bidsSummaryBody = null;
let asksSummaryBody = null;
let outstandingOrdersBody = null;
let recentTradesBody = null;
let spreadValue = null;
let toastContainer = null;

/**
 * Initialize cached references to DOM elements for UI components.
 * Lazy initialization pattern to avoid accessing DOM before it's ready.
 */
function initDOMElements() {
  if (!bidsSummaryBody) bidsSummaryBody = document.getElementById('bids-summary-body');
  if (!asksSummaryBody) asksSummaryBody = document.getElementById('asks-summary-body');
  if (!outstandingOrdersBody) outstandingOrdersBody = document.getElementById('outstanding-orders-body');
  if (!recentTradesBody) recentTradesBody = document.getElementById('recent-trades-body');
  if (!spreadValue) spreadValue = document.getElementById('spread-value');
  if (!toastContainer) toastContainer = document.getElementById('toast-container');
}

/**
 * Show a toast notification on the top right.
 * @param {string} message - Notification text
 * @param {string} type - 'success' or 'error'
 */
export function showToast(message, type = 'success') {
  initDOMElements();
  if (!toastContainer) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const textNode = document.createElement('span');
  textNode.innerText = message;
  toast.appendChild(textNode);

  const closeNode = document.createElement('span');
  closeNode.className = 'toast-close';
  closeNode.innerHTML = '&times;';
  closeNode.onclick = () => {
    toast.style.animation = 'fadeOut 0.3s forwards';
    setTimeout(() => toast.remove(), 300);
  };
  toast.appendChild(closeNode);

  toastContainer.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.animation = 'fadeOut 0.3s forwards';
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
}

/**
 * Render the aggregated Bids and Asks summary tables.
 * @param {Array} summaryData - Aggregated summary levels
 */
export function renderSummaryTables(summaryData) {
  initDOMElements();

  const bids = summaryData.filter(item => item.side === 'BUY').sort((a, b) => b.price - a.price);
  const asks = summaryData.filter(item => item.side === 'SELL').sort((a, b) => a.price - b.price);

  // Calculate spread
  if (bids.length > 0 && asks.length > 0) {
    const highestBid = bids[0].price;
    const lowestAsk = asks[0].price;
    const spread = (lowestAsk - highestBid).toFixed(2);
    if (spreadValue) {
      spreadValue.innerText = `Spread: $${spread} (Bid: $${highestBid.toFixed(2)} | Ask: $${lowestAsk.toFixed(2)})`;
    }
  } else if (spreadValue) {
    spreadValue.innerText = 'Spread: --';
  }

  // Render Bids
  if (bidsSummaryBody) {
    if (bids.length === 0) {
      bidsSummaryBody.innerHTML = `<tr><td colspan="3" class="empty-row">No active bids</td></tr>`;
    } else {
      bidsSummaryBody.innerHTML = bids.map(item => `
        <tr>
          <td>${item.price.toFixed(2)}</td>
          <td>${item.size.toFixed(1)}</td>
          <td>${item.count}</td>
        </tr>
      `).join('');
    }
  }

  // Render Asks
  if (asksSummaryBody) {
    if (asks.length === 0) {
      asksSummaryBody.innerHTML = `<tr><td colspan="3" class="empty-row">No active asks</td></tr>`;
    } else {
      asksSummaryBody.innerHTML = asks.map(item => `
        <tr>
          <td>${item.price.toFixed(2)}</td>
          <td>${item.size.toFixed(1)}</td>
          <td>${item.count}</td>
        </tr>
      `).join('');
    }
  }
}

/**
 * Render Outstanding orders in the tables with Cancel buttons.
 * @param {Object} orderBookData - Current active bids and offers
 */
export function renderOutstandingOrders(orderBookData) {
  initDOMElements();
  if (!outstandingOrdersBody) return;

  const outstandingList = [];

  if (orderBookData.bids) {
    Object.values(orderBookData.bids).forEach(ordersList => {
      ordersList.forEach(ord => outstandingList.push(ord));
    });
  }
  if (orderBookData.offers) {
    Object.values(orderBookData.offers).forEach(ordersList => {
      ordersList.forEach(ord => outstandingList.push(ord));
    });
  }

  outstandingList.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  if (outstandingList.length === 0) {
    outstandingOrdersBody.innerHTML = `<tr><td colspan="6" class="empty-row">No outstanding orders</td></tr>`;
  } else {
    outstandingOrdersBody.innerHTML = outstandingList.map(ord => {
      const badgeClass = ord.side === 'BUY' ? 'badge-buy' : 'badge-sell';
      return `
        <tr>
          <td class="font-mono-val" title="${ord.order_id}">${ord.order_id.substring(0, 10)}</td>
          <td><span class="${badgeClass}">${ord.side}</span></td>
          <td class="font-mono-val">${ord.price.toFixed(2)}</td>
          <td class="font-mono-val">${ord.size.toFixed(1)}</td>
          <td title="${ord.trader_id}">${ord.trader_id}</td>
          <td>
            <button class="btn-cancel" onclick="handleCancelOrder('${ord.order_id}')">Cancel</button>
          </td>
        </tr>
      `;
    }).join('');
  }
}

/**
 * Render executed trades log.
 * @param {Array} tradeData - History list of trades
 */
export function renderRecentTrades(tradeData) {
  initDOMElements();
  if (!recentTradesBody) return;

  const sortedTrades = [...tradeData].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  if (sortedTrades.length === 0) {
    recentTradesBody.innerHTML = `<tr><td colspan="5" class="empty-row">No trades executed yet</td></tr>`;
  } else {
    recentTradesBody.innerHTML = sortedTrades.map(trade => {
      const rowClass = trade.side === 'BUY' ? 'trade-row-buy' : 'trade-row-sell';
      const formattedTime = new Date(trade.timestamp).toLocaleTimeString();
      return `
        <tr class="${rowClass}">
          <td class="font-mono-val" title="${trade.trade_id}">${trade.trade_id.substring(0, 8)}</td>
          <td>${trade.side}</td>
          <td class="font-mono-val">${trade.price.toFixed(2)}</td>
          <td class="font-mono-val">${trade.size.toFixed(1)}</td>
          <td>${formattedTime}</td>
        </tr>
      `;
    }).join('');
  }
}
