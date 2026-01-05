import React from 'react';

const StockCard = ({ name, data, icon }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      maximumFractionDigits: 2
    }).format(price);
  };

  const isPositive = data?.change_percent >= 0;

  return (
    <div className="index-card">
      <div className="index-name">{icon} {name}</div>
      <div className="index-price">{formatPrice(data?.price || 0)}</div>
      <div className={`index-change ${isPositive ? 'change-positive' : 'change-negative'}`}>
        <span>{isPositive ? '▲' : '▼'}</span>
        <span>{Math.abs(data?.change_percent || 0).toFixed(2)}%</span>
      </div>
    </div>
  );
};

export default StockCard;
