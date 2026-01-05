import React, { useState, useEffect, useRef } from 'react';
import { getGoldAnalysis } from '../services/api';
import PredictionCard from './PredictionCard';
import PriceChart from './PriceChart';
import LoadingSpinner from './LoadingSpinner';

const GoldAnalysis = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isMounted = useRef(true);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const fetchAnalysis = async () => {
    if (!isMounted.current) return;

    try {
      setLoading(true);
      const analysisData = await getGoldAnalysis();
      if (isMounted.current) {
        setData(analysisData);
        setError(null);
      }
    } catch (err) {
      if (isMounted.current) {
        setError('Failed to fetch gold analysis. Please try again.');
        console.error('Gold analysis error:', err);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  };

  if (loading) {
    return <LoadingSpinner message="Analyzing gold market..." />;
  }

  if (error) {
    return (
      <div className="error-message">
        <h3>⚠️ Error</h3>
        <p>{error}</p>
        <button onClick={fetchAnalysis} className="chatbot-send-btn">
          Retry
        </button>
      </div>
    );
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(price);
  };

  return (
    <div className="dashboard-container">
      <div style={{ marginBottom: '30px' }}>
        <button 
          onClick={() => window.history.back()}
          className="chatbot-send-btn"
          style={{ marginBottom: '20px' }}
        >
          ← Back to Dashboard
        </button>
        
        <h1 style={{ color: 'white', fontSize: '2rem', marginBottom: '8px' }}>
          🥇 Gold Market Analysis
        </h1>
        <p style={{ color: 'white', opacity: 0.9 }}>
          Current Price: {formatPrice(data?.current_price)} per 10g (24K)
        </p>
      </div>

      <div className="dashboard-grid">
        {/* AI Prediction Card */}
        <div style={{ gridColumn: 'span 1' }}>
          <PredictionCard 
            prediction={data?.ai_analysis?.prediction}
            confidence={data?.ai_analysis?.confidence}
            reasoning={data?.ai_analysis?.reasoning}
            recommendation={data?.ai_analysis?.recommendation}
            risks={data?.ai_analysis?.risks}
          />
        </div>

        {/* Technical Indicators */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#2d3748' }}>
            📈 Technical Indicators
          </h3>
          
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#718096' }}>Current Price:</span>
              <strong>{formatPrice(data?.indicators?.latest_price)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#718096' }}>MA (5-day):</span>
              <strong>{formatPrice(data?.indicators?.ma_5)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#718096' }}>MA (20-day):</span>
              <strong>{formatPrice(data?.indicators?.ma_20)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#718096' }}>MA (50-day):</span>
              <strong>{formatPrice(data?.indicators?.ma_50)}</strong>
            </div>
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '16px 0' }} />

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#718096' }}>RSI (14):</span>
              <strong>{data?.indicators?.rsi?.toFixed(2)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ color: '#718096' }}>MACD:</span>
              <strong>{data?.indicators?.macd?.toFixed(4)}</strong>
            </div>
          </div>
        </div>

        {/* Price Chart */}
        <div style={{ gridColumn: 'span 1' }}>
          <PriceChart data={data?.price_history} />
        </div>

        {/* Market Sentiment */}
        <div className="card">
          <h3 style={{ marginBottom: '20px', color: '#2d3748' }}>
            💭 Market Sentiment
          </h3>
          <p style={{ color: '#4a5568', lineHeight: '1.6' }}>
            {data?.market_sentiment?.summary}
          </p>
        </div>
      </div>
    </div>
  );
};

export default GoldAnalysis;
