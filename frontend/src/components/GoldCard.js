import React from 'react';
import PriceChart from './PriceChart';

const GoldCard = ({ data }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  const getPredictionColor = (prediction) => {
    switch (prediction?.toLowerCase()) {
      case 'bullish':
        return 'prediction-bullish';
      case 'bearish':
        return 'prediction-bearish';
      default:
        return 'prediction-neutral';
    }
  };

  const getPredictionEmoji = (prediction) => {
    switch (prediction?.toLowerCase()) {
      case 'bullish':
        return '🚀';
      case 'bearish':
        return '📉';
      default:
        return '➡️';
    }
  };

  // Debug logging
  React.useEffect(() => {
    console.log('=== GOLD CARD DATA ===');
    console.log('Full data:', data);
    console.log('History array:', data?.history);
    console.log('History length:', data?.history?.length);
    console.log('Tomorrow price:', data?.tomorrow_price);
    console.log('Prediction:', data?.prediction);
    if (data?.history && data.history.length > 0) {
      console.log('First history record:', data.history[0]);
      console.log('Last history record:', data.history[data.history.length - 1]);
    }
  }, [data]);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <span className="card-icon">🥇</span>
          Gold (24K)
        </div>
      </div>

      <div className="price-display">
        {formatPrice(data?.price || 0)}
        <span className="price-unit"> / 10g</span>
      </div>

      <div className={`prediction-badge ${getPredictionColor(data?.prediction)}`}>
        <span>{getPredictionEmoji(data?.prediction)}</span>
        <span>{data?.prediction?.toUpperCase() || 'LOADING'}</span>
      </div>

      <div className="confidence-bar">
        <div className="confidence-label">
          AI Confidence: {data?.confidence?.toFixed(1) || 0}%
        </div>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${data?.confidence || 0}%` }}
          />
        </div>
      </div>

      {/* Tomorrow's Prediction */}
      <div className="tomorrow-forecast">
        <div className="forecast-label">📅 Tomorrow's Predicted Price</div>
        <div className="forecast-price">
          {data?.tomorrow_price ? formatPrice(data.tomorrow_price) : '₹' + (data?.price || 0)}
        </div>
      </div>

      {/* Historical Chart */}
      <div style={{ marginTop: '6px' }}>
        {data?.history && data.history.length > 0 ? (
          <div className="chart-container">
            <PriceChart 
              data={data.history}
              title="30 Days"
              height={120}
            />
          </div>
        ) : (
          <div className="chart-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '130px', background: '#f7fafc', borderRadius: '6px' }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: '#718096', fontSize: '12px', margin: '4px 0' }}>
                📊 Historical Data
              </p>
              <p style={{ color: '#2d3748', fontSize: '13px', fontWeight: 'bold', margin: '4px 0' }}>
                {data?.history?.length || 0}/30
              </p>
              {!data?.history && (
                <p style={{ color: '#e53e3e', fontSize: '11px', margin: '4px 0' }}>
                  ⚠️ No data
                </p>
              )}
              {data?.history?.length === 0 && (
                <p style={{ color: '#ed8936', fontSize: '11px', margin: '4px 0' }}>
                  ⏳ Empty
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GoldCard;
