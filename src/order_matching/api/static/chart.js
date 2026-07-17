let chartOverlayEmpty = null;
let depthChartSvg = null;

function initDOMElements() {
  if (!chartOverlayEmpty) chartOverlayEmpty = document.getElementById('chart-overlay-empty');
  if (!depthChartSvg) depthChartSvg = document.getElementById('depth-chart');
}

/**
 * Render the SVG Depth Chart volume histogram.
 * @param {Array} summaryData - Aggregated price/size summary levels
 */
export function renderDepthChart(summaryData) {
  initDOMElements();
  if (!depthChartSvg) return;

  const bids = summaryData.filter(item => item.side === 'BUY').sort((a, b) => b.price - a.price); // Descending price
  const asks = summaryData.filter(item => item.side === 'SELL').sort((a, b) => a.price - b.price); // Ascending price

  if (bids.length === 0 && asks.length === 0) {
    if (chartOverlayEmpty) chartOverlayEmpty.style.display = 'block';

    // Clear chart paths
    ['depth-bids-area', 'depth-asks-area', 'depth-bids-line', 'depth-asks-line'].forEach(cls => {
      const el = depthChartSvg.querySelector(`.${cls}`);
      if (el) el.setAttribute('d', '');
    });

    const gridLines = depthChartSvg.querySelector('.grid-lines');
    if (gridLines) gridLines.innerHTML = '';

    const centerAxis = depthChartSvg.querySelector('.center-axis');
    if (centerAxis) centerAxis.style.display = 'none';
    return;
  }

  if (chartOverlayEmpty) chartOverlayEmpty.style.display = 'none';

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
  const gridGroup = depthChartSvg.querySelector('.grid-lines');
  if (gridGroup) {
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
  }

  // Draw center axis (between best bid and best ask)
  const centerAxis = depthChartSvg.querySelector('.center-axis');
  if (centerAxis) {
    if (bids.length > 0 && asks.length > 0) {
      const midPrice = (bids[0].price + asks[0].price) / 2;
      const midX = getX(midPrice);
      centerAxis.setAttribute('x1', midX);
      centerAxis.setAttribute('x2', midX);
      centerAxis.style.display = 'block';
    } else {
      centerAxis.style.display = 'none';
    }
  }

  // Build SVG Paths
  let bidsLinePath = '';
  let bidsAreaPath = '';

  if (bidPoints.length > 0) {
    const startX = getX(minPrice);
    const startY = getY(0);

    bidsAreaPath = `M ${startX} ${startY}`;

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

    const bestBidX = getX(bidPoints[0].price);
    bidsAreaPath += ` L ${bestBidX} ${startY} Z`;
  }

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

    const maxPriceX = getX(maxPrice);
    const maxPriceY = getY(askPoints[askPoints.length - 1].cumSize);
    asksLinePath += ` L ${maxPriceX} ${maxPriceY}`;
    asksAreaPath += ` L ${maxPriceX} ${maxPriceY} L ${maxPriceX} ${getY(0)} Z`;
  }

  // Update paths
  const bidsAreaEl = depthChartSvg.querySelector('.depth-bids-area');
  const asksAreaEl = depthChartSvg.querySelector('.depth-asks-area');
  const bidsLineEl = depthChartSvg.querySelector('.depth-bids-line');
  const asksLineEl = depthChartSvg.querySelector('.depth-asks-line');

  if (bidsAreaEl) bidsAreaEl.setAttribute('d', bidsAreaPath);
  if (asksAreaEl) asksAreaEl.setAttribute('d', asksAreaPath);
  if (bidsLineEl) bidsLineEl.setAttribute('d', bidsLinePath);
  if (asksLineEl) asksLineEl.setAttribute('d', asksLinePath);

  // Interactive Tooltip Setup
  setupChartTooltip(getX, getY, bidPoints, askPoints);
}

// INTERACTIVE TOOLTIP LOGIC
function setupChartTooltip(getX, getY, bidPoints, askPoints) {
  initDOMElements();
  if (!depthChartSvg) return;

  const tooltip = depthChartSvg.querySelector('.chart-tooltip');
  const tooltipLine = depthChartSvg.querySelector('.tooltip-line');
  const tooltipCircle = depthChartSvg.querySelector('.tooltip-circle');
  const tooltipBg = depthChartSvg.querySelector('.tooltip-bg');
  const tooltipTextPrice = depthChartSvg.querySelector('.tooltip-text-price');
  const tooltipTextSize = depthChartSvg.querySelector('.tooltip-text-size');

  if (!tooltip || !tooltipLine || !tooltipCircle || !tooltipBg || !tooltipTextPrice || !tooltipTextSize) return;

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
