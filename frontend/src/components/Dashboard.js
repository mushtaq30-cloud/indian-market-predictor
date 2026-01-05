import React, { useState, useEffect, useRef } from 'react';
import { getDashboard } from '../services/api';
import GoldCard from './GoldCard';
import SilverCard from './SilverCard';
import StockCard from './StockCard';
import NewsPanel from './NewsPanel';
import MarketSentiment from './MarketSentiment';
import TopStocks from './TopStocks';
import TopFunds from './TopFunds';
import LoadingSpinner from './LoadingSpinner';

const Dashboard = () => {
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
    // Only fetch once on mount
    const controller = new AbortController();
    fetchDashboard(controller.signal);
    
    // Refresh every 5 minutes
    const interval = setInterval(() => fetchDashboard(null), 300000);
    
    return () => {
      controller.abort();
      clearInterval(interval);
    };
  }, []);

  const fetchDashboard = async (signal) => {
    if (!isMounted.current) return;
    
    try {
      setLoading(true);
      const dashboardData = await getDashboard();
      console.log('════════════════════════════════════════');
      console.log('✅ Dashboard data received');
      console.log('════════════════════════════════════════');
      console.log('Full dashboard:', dashboardData);
      console.log('Gold:', dashboardData?.gold);
      console.log('Gold history:', dashboardData?.gold?.history);
      console.log('Gold history length:', dashboardData?.gold?.history?.length);
      console.log('Silver:', dashboardData?.silver);
      console.log('Silver history:', dashboardData?.silver?.history);
      console.log('Silver history length:', dashboardData?.silver?.history?.length);
      console.log('════════════════════════════════════════');
      
      if (isMounted.current) {
        setData(dashboardData);
        setError(null);
      }
    } catch (err) {
      if (isMounted.current && err.name !== 'AbortError') {
        setError('Failed to fetch dashboard data. Please try again.');
        console.error('Dashboard error:', err);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  };

  if (loading && !data) {
    return <LoadingSpinner message="Loading market data..." />;
  }

  if (error) {
    return (
      <div className="error-message">
        <h3>⚠️ Error</h3>
        <p>{error}</p>
        <button onClick={fetchDashboard} className="chatbot-send-btn">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Market Indices */}
      <div className="market-indices">
        <StockCard 
          name="NIFTY 50"
          data={data?.nifty}
          icon="📈"
        />
        <StockCard 
          name="SENSEX"
          data={data?.sensex}
          icon="📊"
        />
      </div>

      {/* Main Cards Grid */}
      <div className="dashboard-grid">
        <GoldCard data={data?.gold} />
        <SilverCard data={data?.silver} />
        <MarketSentiment sentiment={data?.market_sentiment} aiInsights={data?.ai_insights} />
      </div>

      {/* Top Stock Picks */}
      {data?.top_stocks && (
        <TopStocks data={data?.top_stocks} />
      )}

      {/* Top Mutual Funds */}
      {data?.top_mutual_funds && (
        <TopFunds data={data?.top_mutual_funds} />
      )}

      {/* News Panel */}
      <NewsPanel news={data?.top_news} />
      
      {/* Last Updated */}
      <div style={{ textAlign: 'center', color: '#718096', marginTop: '12px', opacity: 0.8, fontSize: '0.85rem' }}>
        Last updated: {new Date(data?.last_updated).toLocaleString('en-IN')}
      </div>
    </div>
  );
};

export default Dashboard;
