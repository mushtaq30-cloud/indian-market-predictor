import React from 'react';
import './TopStocks.css';

const TopStocks = ({ data }) => {
  if (!data || (!data.top_buys && !data.top_sells)) {
    return (
      <div className="top-stocks-container">
        <h3>📈 Top Stock Picks</h3>
        <p className="loading">Loading stock recommendations...</p>
      </div>
    );
  }

  return (
    <div className="top-stocks-container">
      <div className="stocks-header">
        <h3>📈 Top Stock Picks</h3>
        <span className={`market-trend ${data.market_trend?.toLowerCase()}`}>
          {data.market_trend}
        </span>
      </div>

      <div className="stocks-grid">
        {/* BUY PICKS */}
        <div className="stocks-section">
          <h4 className="section-title bullish">
            🟢 TOP BUYS ({data.top_buys?.length || 0})
          </h4>
          <div className="picks-list">
            {data.top_buys && data.top_buys.length > 0 ? (
              data.top_buys.map((stock, idx) => (
                <div key={idx} className="stock-pick buy">
                  <a href={stock.source_link} target="_blank" rel="noopener noreferrer" className="stock-link">
                  <div className="pick-header">
                    <div className="stock-info">
                      <span className="symbol">{stock.symbol.replace('.NS', '')}</span>
                      <span className="name">{stock.name}</span>
                      <span className="current-price">₹{stock.current_price?.toFixed(2)}</span>
                    </div>
                    <span className="confidence-badge">
                      {stock.confidence}% ✓
                    </span>
                  </div>
                  </a>
                  <div className="pick-body">
                    <div className="target">
                      <span className="label">Target:</span>
                      <span className="target-price bullish">
                        {stock.target_price_change}
                      </span>
                    </div>
                    <p className="reason">{stock.reason}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-picks">No buy recommendations available</p>
            )}
          </div>
        </div>

        {/* SELL PICKS */}
        <div className="stocks-section">
          <h4 className="section-title bearish">
            🔴 TOP SELLS ({data.top_sells?.length || 0})
          </h4>
          <div className="picks-list">
            {data.top_sells && data.top_sells.length > 0 ? (
              data.top_sells.map((stock, idx) => (
                <div key={idx} className="stock-pick sell">
                  <a href={stock.source_link} target="_blank" rel="noopener noreferrer" className="stock-link">
                  <div className="pick-header">
                    <div className="stock-info">
                      <span className="symbol">{stock.symbol.replace('.NS', '')}</span>
                      <span className="name">{stock.name}</span>
                      <span className="current-price">₹{stock.current_price?.toFixed(2)}</span>
                    </div>
                    <span className="confidence-badge">
                      {stock.confidence}% ✗
                    </span>
                  </div>
                  </a>
                  <div className="pick-body">
                    <div className="target">
                      <span className="label">Target:</span>
                      <span className="target-price bearish">
                        {stock.target_price_change}
                      </span>
                    </div>
                    <p className="reason">{stock.reason}</p>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-picks">No sell recommendations available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TopStocks;
