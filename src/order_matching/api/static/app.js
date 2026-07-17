/* eslint-env browser */

// API BASE URL
const API_BASE = window.location.origin;

// STATE
let refreshTimer = null;
let orderBookData = { bids: {}, offers: {} };
let summaryData = [];
let tradeData = [];

// DOM ELEMENTS
const orderForm = document.getElementById('order-form');
const btnGenId = document.getElementById('btn-gen-id');
const orderIdInput = document.getElementById('order-id');
const orderPriceInput = document.getElementById('order-price');
const orderSizeInput = document.getElementById('order-size');
const orderTimestampInput = document.getElementById('order-timestamp');
const autoTimestampCheckbox = document.getElementById('auto-timestamp');

const matchAutoTimestampCheckbox = document.getElementById('match-auto-timestamp');
const matchTimestampInput = document.getElementById('match-timestamp');
const btnMatch = document.getElementById('btn-match');

const btnReset = document.getElementById('btn-reset');
const resetModal = document.getElementById('reset-modal');
const modalClose = document.querySelector('.modal-close');
const btnModalCancel = document.getElementById('btn-modal-cancel');
const btnModalConfirm = document.getElementById('btn-modal-confirm');
const resetSeedInput = document.getElementById('reset-seed');
const resetPrepopulateCheckbox = document.getElementById('reset-prepopulate');

const bidsSummaryBody = document.getElementById('bids-summary-body');
const asksSummaryBody = document.getElementById('asks-summary-body');
const outstandingOrdersBody = document.getElementById('outstanding-orders-body');
const recentTradesBody = document.getElementById('recent-trades-body');

const spreadValue = document.getElementById('spread-value');
const chartOverlayEmpty = document.getElementById('chart-overlay-empty');
const depthChartSvg = document.getElementById('depth-chart');
const toastContainer = document.getElementById('toast-container');

// INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
  generateAndSetOrderId();
  updateTimestampInputs();

  // Set intervals for input updates
  setInterval(updateTimestampInputs, 1000);

  // Attach Event Listeners
  setupEventListeners();

  // Initial fetch
  refreshDashboard();

  // Start Polling (every 1 second)
  startPolling();
});

// EVENT LISTENERS SETUP
function setupEventListeners() {
  // Generate random order ID
  btnGenId.addEventListener('click', generateAndSetOrderId);

  // Form submission
  orderForm.addEventListener('submit', handleOrderSubmit);

  // Order Type Toggle (disable price for market orders)
  document.getElementsByName('order_type').forEach(radio => {
    radio.addEventListener('change', (e) => {
      const isMarket = e.target.value === 'market';
      orderPriceInput.disabled = isMarket;
      if (isMarket) {
        orderPriceInput.value = '';
        orderPriceInput.removeAttribute('required');
      } else {
        orderPriceInput.value = '100.0';
        orderPriceInput.setAttribute('required', 'required');
      }
    });
  });

  // Toggle auto timestamps
  autoTimestampCheckbox.addEventListener('change', () => {
    orderTimestampInput.disabled = autoTimestampCheckbox.checked;
    updateTimestampInputs();
  });

  matchAutoTimestampCheckbox.addEventListener('change', () => {
    matchTimestampInput.disabled = matchAutoTimestampCheckbox.checked;
    updateTimestampInputs();
  });

  // Match runner
  btnMatch.addEventListener('click', handleMatchTrigger);

  // Reset modal logic
  btnReset.addEventListener('click', () => {
    resetModal.style.display = 'flex';
  });

  const closeModal = () => {
    resetModal.style.display = 'none';
  };

  modalClose.addEventListener('click', closeModal);
  btnModalCancel.addEventListener('click', closeModal);

  window.addEventListener('click', (e) => {
    if (e.target === resetModal) closeModal();
  });

  btnModalConfirm.addEventListener('click', () => {
    const seed = resetSeedInput.value ? parseInt(resetSeedInput.value) : null;
    const prepopulate = resetPrepopulateCheckbox.checked;
    handleReset(seed, prepopulate);
    closeModal();
  });
}

// TIMESTAMPS
function updateTimestampInputs() {
  const now = new Date();
  // Format to local ISO-like string for datetime-local input: YYYY-MM-DDTHH:MM:SS
  const formatLocalISO = (date) => {
    const pad = (num) => String(num).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  };

  if (autoTimestampCheckbox.checked) {
    orderTimestampInput.value = formatLocalISO(now);
  }

  if (matchAutoTimestampCheckbox.checked) {
    matchTimestampInput.value = formatLocalISO(now);
  }
}

function generateAndSetOrderId() {
  const randomNum = Math.floor(1000 + Math.random() * 9000);
  orderIdInput.value = `ord_${randomNum}`;
}

// POLLING STATE MANAGEMENT
function startPolling() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(refreshDashboard, 1000);
}



// TOAST NOTIFICATIONS
function showToast(message, type = 'success') {
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

  // Auto-remove after 4 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.animation = 'fadeOut 0.3s forwards';
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
}

// API OPERATIONS
async function handleOrderSubmit(e) {
  e.preventDefault();

  const side = document.querySelector('input[name="side"]:checked').value;
  const orderType = document.querySelector('input[name="order_type"]:checked').value;
  const orderId = orderIdInput.value.trim();
  const traderId = document.getElementById('trader-id').value.trim();
  const size = parseFloat(orderSizeInput.value);

  // Ensure timestamp is properly formatted as full ISO string for Pydantic
  let timestampStr;
  if (autoTimestampCheckbox.checked) {
    timestampStr = new Date().toISOString();
  } else {
    timestampStr = new Date(orderTimestampInput.value).toISOString();
  }

  const orderPayload = {
    order_type: orderType,
    order_id: orderId,
    trader_id: traderId,
    side: side,
    size: size,
    timestamp: timestampStr
  };

  if (orderType === 'limit') {
    orderPayload.price = parseFloat(orderPriceInput.value);
  }

  try {
    const res = await fetch(`${API_BASE}/place`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ orders: [orderPayload] })
    });

    const data = await res.json();

    if (res.ok) {
      showToast(data.message || 'Order placed successfully!', 'success');
      generateAndSetOrderId();
      // Keep quantity and trader_id, but update dashboard immediately
      refreshDashboard();
    } else {
      let errMsg = 'Failed to place order';
      if (data.detail) {
        if (Array.isArray(data.detail)) {
          errMsg = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(' | ');
        } else {
          errMsg = data.detail;
        }
      }
      showToast(errMsg, 'error');
    }
  } catch (err) {
    showToast(`Network error: ${err.message}`, 'error');
  }
}

async function handleCancelOrder(orderId) {
  try {
    const res = await fetch(`${API_BASE}/orders/${orderId}`, {
      method: 'DELETE'
    });
    const data = await res.json();

    if (res.ok) {
      showToast(`Order ${orderId} cancelled successfully!`, 'success');
      refreshDashboard();
    } else {
      showToast(data.detail || 'Failed to cancel order', 'error');
    }
  } catch (err) {
    showToast(`Network error: ${err.message}`, 'error');
  }
}
window.handleCancelOrder = handleCancelOrder;

async function handleMatchTrigger() {
  let timestampStr;
  if (matchAutoTimestampCheckbox.checked) {
    timestampStr = new Date().toISOString();
  } else {
    timestampStr = new Date(matchTimestampInput.value).toISOString();
  }

  try {
    const res = await fetch(`${API_BASE}/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timestamp: timestampStr })
    });

    const data = await res.json();

    if (res.ok) {
      const tradeCount = data.trades ? data.trades.length : 0;
      if (tradeCount > 0) {
        showToast(`Match executed! Filled ${tradeCount} trade(s).`, 'success');
      } else {
        showToast('Matching completed. No overlapping orders crossed.', 'success');
      }
      refreshDashboard();
    } else {
      showToast(data.detail || 'Failed to execute matching', 'error');
    }
  } catch (err) {
    showToast(`Network error: ${err.message}`, 'error');
  }
}

async function handleReset(seed, prepopulate) {
  try {
    const res = await fetch(`${API_BASE}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ seed: seed, prepopulate: prepopulate })
    });
    const data = await res.json();

    if (res.ok) {
      showToast(data.message || 'Market state reset successfully!', 'success');
      refreshDashboard();
    } else {
      showToast(data.detail || 'Failed to reset market state', 'error');
    }
  } catch (err) {
    showToast(`Network error: ${err.message}`, 'error');
  }
}

// DASHBOARD REFRESH
async function refreshDashboard() {
  try {
    // Parallel fetches
    const [ordersRes, tradesRes, summaryRes] = await Promise.all([
      fetch(`${API_BASE}/orders`),
      fetch(`${API_BASE}/trades`),
      fetch(`${API_BASE}/summary`)
    ]);

    if (ordersRes.ok) orderBookData = await ordersRes.json();
    if (tradesRes.ok) tradeData = (await tradesRes.json()).trades;
    if (summaryRes.ok) summaryData = await summaryRes.json();

    // Update individual UI panels
    renderSummaryTables();
    renderOutstandingOrders();
    renderRecentTrades();
    renderDepthChart();
  } catch (err) {
    console.error('Failed to poll dashboard data:', err);
  }
}

// RENDER SUMMARY TABLES
function renderSummaryTables() {
  const bids = summaryData.filter(item => item.side === 'BUY').sort((a, b) => b.price - a.price);
  const asks = summaryData.filter(item => item.side === 'SELL').sort((a, b) => a.price - b.price);

  // Calculate spread
  if (bids.length > 0 && asks.length > 0) {
    const highestBid = bids[0].price;
    const lowestAsk = asks[0].price;
    const spread = (lowestAsk - highestBid).toFixed(2);
    spreadValue.innerText = `Spread: $${spread} (Bid: $${highestBid.toFixed(2)} | Ask: $${lowestAsk.toFixed(2)})`;
  } else {
    spreadValue.innerText = 'Spread: --';
  }

  // Render Bids
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

  // Render Asks
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

// RENDER OUTSTANDING ORDERS LIST
function renderOutstandingOrders() {
  const outstandingList = [];

  // Extract orders from get_orders response
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

  // Sort outstanding orders by timestamp descending so newest are on top
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

// RENDER RECENT TRADES FEED
function renderRecentTrades() {
  // Sort trades by timestamp descending
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

// RENDER SVG DEPTH CHART
function renderDepthChart() {
  const bids = summaryData.filter(item => item.side === 'BUY').sort((a, b) => b.price - a.price); // Descending price
  const asks = summaryData.filter(item => item.side === 'SELL').sort((a, b) => a.price - b.price); // Ascending price

  if (bids.length === 0 && asks.length === 0) {
    chartOverlayEmpty.style.display = 'block';
    // Clear chart paths
    ['depth-bids-area', 'depth-asks-area', 'depth-bids-line', 'depth-asks-line'].forEach(cls => {
      document.querySelector(`.${cls}`).setAttribute('d', '');
    });
    document.querySelector('.grid-lines').innerHTML = '';
    document.querySelector('.center-axis').style.display = 'none';
    return;
  }

  chartOverlayEmpty.style.display = 'none';

  // Construct cumulative lists
  let cumBidVol = 0;
  const bidPoints = bids.map(b => {
    cumBidVol += b.size;
    return { price: b.price, cumSize: cumBidVol };
  });

  let cumAskVol = 0;
  const askPoints = asks.map(a => {
    cumAskVol += a.size;
    return { price: a.price, cumSize: cumAskVol };
  });

  const maxVolume = Math.max(cumBidVol, cumAskVol, 1);

  // Find price bounds
  const prices = summaryData.map(item => item.price);
  const minPrice = Math.min(...prices) * 0.995; // Add 0.5% margin
  const maxPrice = Math.max(...prices) * 1.005;
  const priceRange = maxPrice - minPrice;

  // SVG coordinates converter helper
  const svgWidth = 600;
  const svgHeight = 240;
  const marginY = 20;
  const chartHeight = svgHeight - marginY;

  const getX = (price) => {
    return ((price - minPrice) / priceRange) * svgWidth;
  };

  const getY = (volume) => {
    return chartHeight - (volume / maxVolume) * (chartHeight - marginY);
  };

  // Render grid lines & price ticks
  const gridGroup = document.querySelector('.grid-lines');
  gridGroup.innerHTML = '';

  // Calculate price ticks
  const tickCount = 5;
  const step = priceRange / (tickCount - 1);
  for (let i = 0; i < tickCount; i++) {
    const priceTick = minPrice + i * step;
    const x = getX(priceTick);

    // Draw vertical grid line
    const gridLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    gridLine.setAttribute('x1', x);
    gridLine.setAttribute('y1', 0);
    gridLine.setAttribute('x2', x);
    gridLine.setAttribute('y2', chartHeight);
    gridGroup.appendChild(gridLine);

    // Draw text label
    const textLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    textLabel.setAttribute('x', x);
    textLabel.setAttribute('y', svgHeight - 4);
    textLabel.setAttribute('text-anchor', i === 0 ? 'start' : i === tickCount - 1 ? 'end' : 'middle');
    textLabel.textContent = priceTick.toFixed(1);
    gridGroup.appendChild(textLabel);
  }

  // Draw center axis (between best bid and best ask)
  const centerAxis = document.querySelector('.center-axis');
  if (bids.length > 0 && asks.length > 0) {
    const midPrice = (bids[0].price + asks[0].price) / 2;
    const midX = getX(midPrice);
    centerAxis.setAttribute('x1', midX);
    centerAxis.setAttribute('x2', midX);
    centerAxis.style.display = 'block';
  } else {
    centerAxis.style.display = 'none';
  }

  // Build SVG Paths
  // Bids step chart (descending prices)
  let bidsLinePath = '';
  let bidsAreaPath = '';

  if (bidPoints.length > 0) {
    // Start at bottom left (minPrice)
    const startX = getX(minPrice);
    const startY = getY(0);

    bidsAreaPath = `M ${startX} ${startY}`;

    // Draw steps
    // For bids, we go from highest bid down to lowest bid (min price)
    // We reverse points to build the step line from minPrice (left) to best bid (right)
    const revBidPoints = [...bidPoints].reverse();

    revBidPoints.forEach((pt, i) => {
      const x = getX(pt.price);
      const y = getY(pt.cumSize);

      if (i === 0) {
        bidsLinePath = `M ${startX} ${y} L ${x} ${y}`;
        bidsAreaPath += ` L ${startX} ${y} L ${x} ${y}`;
      } else {
        bidsLinePath += ` L ${x} ${getY(revBidPoints[i - 1].cumSize)} L ${x} ${y}`;
        bidsAreaPath += ` L ${x} ${getY(revBidPoints[i - 1].cumSize)} L ${x} ${y}`;
      }
    });

    // End the line at the best bid price (on the right)
    const bestBidX = getX(bidPoints[0].price);

    // Close the area path down to the bottom
    bidsAreaPath += ` L ${bestBidX} ${startY} Z`;
  }

  // Asks step chart (ascending prices)
  let asksLinePath = '';
  let asksAreaPath = '';

  if (askPoints.length > 0) {
    const startX = getX(askPoints[0].price);
    const startY = getY(0);

    asksAreaPath = `M ${startX} ${startY}`;

    askPoints.forEach((pt, i) => {
      const x = getX(pt.price);
      const y = getY(pt.cumSize);

      if (i === 0) {
        asksLinePath = `M ${startX} ${y} L ${x} ${y}`;
        asksAreaPath += ` L ${startX} ${y} L ${x} ${y}`;
      } else {
        asksLinePath += ` L ${x} ${getY(askPoints[i - 1].cumSize)} L ${x} ${y}`;
        asksAreaPath += ` L ${x} ${getY(askPoints[i - 1].cumSize)} L ${x} ${y}`;
      }
    });

    // Extend asks to the max price on the right
    const maxPriceX = getX(maxPrice);
    const maxPriceY = getY(askPoints[askPoints.length - 1].cumSize);
    asksLinePath += ` L ${maxPriceX} ${maxPriceY}`;
    asksAreaPath += ` L ${maxPriceX} ${maxPriceY} L ${maxPriceX} ${getY(0)} Z`;
  }

  // Update paths
  document.querySelector('.depth-bids-area').setAttribute('d', bidsAreaPath);
  document.querySelector('.depth-asks-area').setAttribute('d', asksAreaPath);
  document.querySelector('.depth-bids-line').setAttribute('d', bidsLinePath);
  document.querySelector('.depth-asks-line').setAttribute('d', asksLinePath);

  // Interactive Tooltip Setup
  setupChartTooltip(getX, getY, bidPoints, askPoints);
}

// INTERACTIVE TOOLTIP LOGIC
function setupChartTooltip(getX, getY, bidPoints, askPoints) {
  const tooltip = document.querySelector('.chart-tooltip');
  const tooltipLine = document.querySelector('.tooltip-line');
  const tooltipCircle = document.querySelector('.tooltip-circle');
  const tooltipBg = document.querySelector('.tooltip-bg');
  const tooltipTextPrice = document.querySelector('.tooltip-text-price');
  const tooltipTextSize = document.querySelector('.tooltip-text-size');

  // Combined points for tooltip lookup
  const allPoints = [
    ...bidPoints.map(p => ({ ...p, side: 'BUY' })),
    ...askPoints.map(p => ({ ...p, side: 'SELL' }))
  ];

  depthChartSvg.onmousemove = (e) => {
    if (allPoints.length === 0) return;

    // Get mouse coordinates relative to SVG
    const rect = depthChartSvg.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const scaledMouseX = (mouseX / rect.width) * 600; // Map screen width to viewport 600

    // Find closest point by price (closest X coordinate)
    let closestPt = null;
    let minDistance = Infinity;

    allPoints.forEach(pt => {
      const ptX = getX(pt.price);
      const dist = Math.abs(ptX - scaledMouseX);
      if (dist < minDistance) {
        minDistance = dist;
        closestPt = pt;
      }
    });

    if (closestPt && minDistance < 50) {
      const x = getX(closestPt.price);
      const y = getY(closestPt.cumSize);

      // Position vertical line & circle dot
      tooltipLine.setAttribute('x1', x);
      tooltipLine.setAttribute('x2', x);
      tooltipCircle.setAttribute('cx', x);
      tooltipCircle.setAttribute('cy', y);
      tooltipCircle.setAttribute('fill', closestPt.side === 'BUY' ? 'var(--color-buy)' : 'var(--color-sell)');

      // Populate text
      tooltipTextPrice.textContent = `Price: $${closestPt.price.toFixed(2)}`;
      tooltipTextSize.textContent = `Cum Size: ${closestPt.cumSize.toFixed(1)}`;

      // Position tooltip box to avoid going off screen
      let boxX = x + 10;
      if (boxX > 470) boxX = x - 130;
      let boxY = y - 60;
      if (boxY < 10) boxY = y + 10;

      tooltipBg.setAttribute('x', boxX);
      tooltipBg.setAttribute('y', boxY);
      tooltipTextPrice.setAttribute('x', boxX + 10);
      tooltipTextPrice.setAttribute('y', boxY + 20);
      tooltipTextSize.setAttribute('x', boxX + 10);
      tooltipTextSize.setAttribute('y', boxY + 40);

      tooltip.style.display = 'block';
    } else {
      tooltip.style.display = 'none';
    }
  };

  depthChartSvg.onmouseleave = () => {
    tooltip.style.display = 'none';
  };
}
