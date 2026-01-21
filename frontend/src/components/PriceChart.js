import React from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

const PriceChart = ({ data, title, dataKey = 'price_inr', color = '#667eea', height = 120 }) => {
  React.useEffect(() => {
    console.log('🎨 PriceChart rendered with:', {
      dataLength: data?.length,
      dataKey,
      height,
      hasData: !!data && data.length > 0,
      firstRecord: data?.[0],
      title
    });
  }, [data, dataKey, height, title]);

  if (!data || data.length === 0) {
    console.warn('❌ PriceChart: No data provided', { data, dataLength: data?.length });
    return (
      <div style={{ textAlign: 'center', padding: '8px', color: '#a0aec0', fontSize: '10px' }}>
        📊 No data
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
  };

  // Compact price format for Y-axis (e.g., "₹120K" or "₹95K")
  const formatPriceCompact = (value) => {
    if (value >= 100000) {
      return '₹' + (value / 1000).toFixed(0) + 'K';
    } else if (value >= 1000) {
      return '₹' + (value / 1000).toFixed(1) + 'K';
    }
    return '₹' + value.toFixed(0);
  };

  const formatPrice = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div style={{ width: '100%' }}>
      {title && (
        <h4 style={{
          margin: '0 0 2px 0',
          color: document.body.classList.contains('dark-mode') ? '#cbd5e0' : '#718096',
          fontSize: '0.75rem',
          fontWeight: '600'
        }}>
          {title}
        </h4>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 10, right: 5, left: 3, bottom: 18 }}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.5}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>

          <CartesianGrid stroke="none" vertical={false} />

          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke="none"
            tick={{ fontSize: 10, fill: document.body.classList.contains('dark-mode') ? '#a0aec0' : '#cbd5e0' }}
            interval={Math.floor(Math.max(0, data.length - 4))}
            axisLine={false}
          />

          <YAxis
            domain={[
              (dataMin) => dataMin * 0.98,
              (dataMax) => dataMax * 1.02
            ]}
            tickFormatter={formatPriceCompact}
            stroke="none"
            tick={{ fontSize: 10, fill: document.body.classList.contains('dark-mode') ? '#a0aec0' : '#cbd5e0' }}
            width={45}
            axisLine={false}
          />

          <Tooltip
            formatter={(value) => formatPrice(value)}
            labelFormatter={formatDate}
            contentStyle={{
              background: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #cbd5e0',
              borderRadius: '4px',
              padding: '6px',
              fontSize: '10px'
            }}
          />

          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={1.8}
            fillOpacity={1}
            fill="url(#colorPrice)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceChart;
