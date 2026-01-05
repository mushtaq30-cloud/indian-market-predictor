import React from 'react';

const PredictionCard = ({ prediction, confidence, reasoning, recommendation, risks }) => {
  const getPredictionStyle = () => {
    switch (prediction?.toLowerCase()) {
      case 'bullish':
        return {
          background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
          icon: '🚀',
          text: 'BULLISH'
        };
      case 'bearish':
        return {
          background: 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)',
          icon: '📉',
          text: 'BEARISH'
        };
      default:
        return {
          background: 'linear-gradient(135deg, #ed8936 0%, #dd6b20 100%)',
          icon: '➡️',
          text: 'NEUTRAL'
        };
    }
  };

  const style = getPredictionStyle();

  return (
    <div className="card" style={{ marginBottom: '20px' }}>
      <div style={{
        ...style,
        background: style.background,
        color: 'white',
        padding: '24px',
        borderRadius: '12px',
        marginBottom: '20px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '3rem', marginBottom: '8px' }}>
          {style.icon}
        </div>
        <div style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '8px' }}>
          {style.text}
        </div>
        <div style={{ fontSize: '1.1rem', opacity: 0.95 }}>
          AI Confidence: {confidence?.toFixed(1)}%
        </div>
      </div>

      {recommendation && (
        <div style={{
          background: '#f7fafc',
          padding: '16px',
          borderRadius: '12px',
          marginBottom: '20px'
        }}>
          <div style={{ fontWeight: 600, marginBottom: '12px', color: '#2d3748', fontSize: '1.1rem' }}>
            💡 Recommendation
          </div>
          <div style={{ color: '#4a5568', lineHeight: 1.6 }}>
            <div><strong>Action:</strong> {recommendation.action}</div>
            {recommendation.position_size && (
              <div style={{ marginTop: '4px' }}>
                <strong>Position Size:</strong> {recommendation.position_size}
              </div>
            )}
            {recommendation.stop_loss && (
              <div style={{ marginTop: '4px' }}>
                <strong>Stop Loss:</strong> {recommendation.stop_loss}
              </div>
            )}
            {recommendation.target_price && (
              <div style={{ marginTop: '4px' }}>
                <strong>Target Price:</strong> {recommendation.target_price}
              </div>
            )}
          </div>
        </div>
      )}

      {reasoning && reasoning.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontWeight: 600, marginBottom: '12px', color: '#2d3748', fontSize: '1.1rem' }}>
            📊 Key Reasoning
          </div>
          <ul style={{ paddingLeft: '20px', color: '#4a5568', lineHeight: 1.8 }}>
            {reasoning.map((reason, idx) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      {risks && risks.length > 0 && (
        <div>
          <div style={{ fontWeight: 600, marginBottom: '12px', color: '#2d3748', fontSize: '1.1rem' }}>
            ⚠️ Risks to Watch
          </div>
          <ul style={{ paddingLeft: '20px', color: '#e53e3e', lineHeight: 1.8 }}>
            {risks.map((risk, idx) => (
              <li key={idx}>{risk}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PredictionCard;
