import React from 'react';
import './TopFunds.css';

const TopFunds = ({ data }) => {
  if (!data || !data.top_funds) {
    return (
      <div className="top-funds-container">
        <h3>💰 Top Mutual Funds</h3>
        <p className="loading">Loading mutual fund data...</p>
      </div>
    );
  }

  return (
    <div className="top-funds-container">
      <div className="funds-header">
        <div className="header-left">
          <h3>💰 Top Mutual Funds</h3>
          <p className="investment-insight">{data.investment_insight}</p>
        </div>
        <div className="header-right">
          <div className="total-aum">
            <span className="label">Total AUM:</span>
            <span className="value">{data.total_aum}</span>
          </div>
        </div>
      </div>

      <div className="funds-grid">
        {data.top_funds && data.top_funds.length > 0 ? (
          data.top_funds.map((fund, idx) => (
            <div key={idx} className="fund-card">
              <div className="fund-rank">
                {idx === 0 && '🥇'}
                {idx === 1 && '🥈'}
                {idx === 2 && '🥉'}
                {idx > 2 && `#${idx + 1}`}
              </div>
              
              <h4 className="fund-name">{fund.name}</h4>
              
              <div className="fund-meta">
                <span className="type-badge">{fund.type}</span>
                <span className="rating-badge">{fund.rating}</span>
              </div>

              <div className="fund-stats">
                <div className="stat">
                  <span className="stat-label">1Yr Return</span>
                  <span className="stat-value bullish">
                    +{fund.return_1yr.toFixed(1)}%
                  </span>
                </div>
                <div className="stat">
                  <span className="stat-label">AUM</span>
                  <span className="stat-value">{fund.aum}</span>
                </div>
              </div>

              <button className="invest-btn">View Details</button>
            </div>
          ))
        ) : (
          <p className="no-funds">No mutual fund data available</p>
        )}
      </div>

      {/* Fund Categories */}
      {data.categories && (Object.keys(data.categories).length > 0) && (
        <div className="fund-categories">
          <h4 className="categories-title">💼 Recommended by Category</h4>
          
          <div className="categories-grid">
            {data.categories.large_cap && data.categories.large_cap.length > 0 && (
              <div className="category-section">
                <h5>📈 Large Cap (40%)</h5>
                <ul className="category-list">
                  {data.categories.large_cap.map((fund, idx) => (
                    <li key={idx}>
                      <span className="fund-shortname">
                        {fund.name.split(' ').slice(0, 2).join(' ')}
                      </span>
                      <span className="fund-return">+{fund.return_1yr.toFixed(1)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {data.categories.multi_cap && data.categories.multi_cap.length > 0 && (
              <div className="category-section">
                <h5>🎯 Multi Cap (30%)</h5>
                <ul className="category-list">
                  {data.categories.multi_cap.map((fund, idx) => (
                    <li key={idx}>
                      <span className="fund-shortname">
                        {fund.name.split(' ').slice(0, 2).join(' ')}
                      </span>
                      <span className="fund-return">+{fund.return_1yr.toFixed(1)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TopFunds;
