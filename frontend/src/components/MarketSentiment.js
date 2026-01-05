import React from 'react';

const MarketSentiment = ({ sentiment, aiInsights }) => {
  const getSentimentColor = (label) => {
    switch (label?.toLowerCase()) {
      case 'positive':
        return 'sentiment-positive';
      case 'negative':
        return 'sentiment-negative';
      default:
        return 'sentiment-neutral';
    }
  };

  const getSentimentEmoji = (label) => {
    switch (label?.toLowerCase()) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😟';
      default:
        return '😐';
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <span className="card-icon">💭</span>
          Market Sentiment
        </div>
      </div>

      <div className="sentiment-indicator">
        <div className="sentiment-icon">
          {getSentimentEmoji(sentiment?.label)}
        </div>
        <div className="sentiment-details">
          <div className={`sentiment-label ${getSentimentColor(sentiment?.label)}`}>
            {sentiment?.label?.toUpperCase() || 'NEUTRAL'}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#718096' }}>
            Score: {sentiment?.overall_sentiment?.toFixed(3) || '0.000'}
          </div>
        </div>
      </div>

      <div style={{ 
        marginTop: '16px', 
        padding: '16px', 
        background: '#f7fafc', 
        borderRadius: '12px',
        fontSize: '0.95rem',
        lineHeight: '1.6'
      }}>
        <div style={{ fontWeight: 600, marginBottom: '8px', color: '#2d3748' }}>
          🤖 AI Market Insights:
        </div>
        <div style={{ color: '#4a5568' }}>
          {aiInsights || 'Analyzing market conditions...'}
        </div>
      </div>

      <div style={{ 
        marginTop: '16px', 
        display: 'flex', 
        justifyContent: 'space-between',
        fontSize: '0.85rem',
        color: '#718096'
      }}>
        <span>✅ Positive: {sentiment?.positive_count || 0}</span>
        <span>❌ Negative: {sentiment?.negative_count || 0}</span>
        <span>➖ Neutral: {sentiment?.neutral_count || 0}</span>
      </div>
    </div>
  );
};

export default MarketSentiment;
