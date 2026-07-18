import {
  placeOrder,
  cancelOrder,
  matchOrders,
  resetEngine,
  fetchMarketState
} from './api.js';
import {
  showToast,
  renderSummaryTables,
  renderOutstandingOrders,
  renderRecentTrades
} from './ui.js';
import { renderDepthChart } from './chart.js';

// STATE
let refreshTimer = null;
let isMatchingActive = true;

// DOM ELEMENTS
const btnToggleEngine = document.getElementById('btn-toggle-engine');
const engineStatusDot = document.getElementById('engine-status-dot');
const engineStatusText = document.getElementById('engine-status-text');
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

  // Toggle engine online/paused
  btnToggleEngine.addEventListener('click', toggleAutoMatching);

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
    handleReset(seed, false);
    closeModal();
  });
}

function toggleAutoMatching() {
  isMatchingActive = !isMatchingActive;
  if (isMatchingActive) {
    btnToggleEngine.classList.remove('paused');
    engineStatusDot.className = 'status-dot pulsing';
    engineStatusText.innerText = 'Engine Online';
    showToast('Auto-matching resumed', 'success');
  } else {
    btnToggleEngine.classList.add('paused');
    engineStatusDot.className = 'status-dot';
    engineStatusText.innerText = 'Engine Paused';
    showToast('Auto-matching paused', 'success');
  }
}

// TIMESTAMPS
function updateTimestampInputs() {
  const now = new Date();
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

// POLLING & AUTOMATIC MATCHING MANAGEMENT
function startPolling() {
  if (refreshTimer) clearTimeout(refreshTimer);
  refreshTimer = setTimeout(tick, 1000);
}

async function tick() {
  if (isMatchingActive) {
    try {
      await matchOrders(new Date().toISOString());
    } catch (err) {
      console.warn('Silent auto-matching run skipped or failed:', err);
    }
  }
  await refreshDashboard();
  refreshTimer = setTimeout(tick, 1000);
}

// API OPERATIONS
async function handleOrderSubmit(e) {
  e.preventDefault();

  const side = document.querySelector('input[name="side"]:checked').value;
  const orderType = document.querySelector('input[name="order_type"]:checked').value;
  const orderId = orderIdInput.value.trim();
  const traderId = document.getElementById('trader-id').value.trim();
  const size = parseFloat(orderSizeInput.value);

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
    const data = await placeOrder(orderPayload);
    showToast(data.message || 'Order placed successfully!', 'success');
    generateAndSetOrderId();
    refreshDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleCancelOrder(orderId) {
  try {
    await cancelOrder(orderId);
    showToast(`Order ${orderId} cancelled successfully!`, 'success');
    refreshDashboard();
  } catch (err) {
    showToast(err.message, 'error');
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
    const data = await matchOrders(timestampStr);
    const tradeCount = data.trades ? data.trades.length : 0;
    if (tradeCount > 0) {
      showToast(`Match executed! Filled ${tradeCount} trade(s).`, 'success');
    } else {
      showToast('Matching completed. No overlapping orders crossed.', 'success');
    }
    refreshDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleReset(seed, prepopulate) {
  try {
    const data = await resetEngine(seed, prepopulate);
    showToast(data.message || 'Market state reset successfully!', 'success');
    refreshDashboard();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// DASHBOARD REFRESH
async function refreshDashboard() {
  try {
    const { orderBookData, tradeData, summaryData } = await fetchMarketState();

    renderSummaryTables(summaryData);
    renderOutstandingOrders(orderBookData);
    renderRecentTrades(tradeData);
    renderDepthChart(summaryData);
  } catch (err) {
    console.error('Failed to poll dashboard data:', err);
  }
}
