import React from 'react';

const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <div className="loading-spinner">
      <div>
        <div className="spinner"></div>
        <div style={{ marginTop: '20px', color: 'white', fontSize: '1.1rem' }}>
          {message}
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
