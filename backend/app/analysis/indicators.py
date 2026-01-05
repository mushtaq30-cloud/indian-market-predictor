import pandas as pd
import numpy as np
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def calculate_moving_averages(df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
    """Calculate various moving averages"""
    df['ma_5'] = df[price_col].rolling(window=5).mean()
    df['ma_10'] = df[price_col].rolling(window=10).mean()
    df['ma_20'] = df[price_col].rolling(window=20).mean()
    df['ma_50'] = df[price_col].rolling(window=50).mean()
    df['ma_100'] = df[price_col].rolling(window=100).mean()
    df['ma_200'] = df[price_col].rolling(window=200).mean()
    
    return df

def calculate_ema(df: pd.DataFrame, price_col: str = 'price', spans: list = [12, 26, 50]) -> pd.DataFrame:
    """Calculate Exponential Moving Averages"""
    for span in spans:
        df[f'ema_{span}'] = df[price_col].ewm(span=span, adjust=False).mean()
    
    return df

def calculate_rsi(df: pd.DataFrame, price_col: str = 'price', period: int = 14) -> pd.DataFrame:
    """
    Calculate Relative Strength Index (RSI)
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss
    """
    delta = df[price_col].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df

def calculate_macd(df: pd.DataFrame, price_col: str = 'price') -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    MACD Line: 12-day EMA - 26-day EMA
    Signal Line: 9-day EMA of MACD
    Histogram: MACD - Signal
    """
    df['ema_12'] = df[price_col].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df[price_col].ewm(span=26, adjust=False).mean()
    
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

def calculate_bollinger_bands(df: pd.DataFrame, price_col: str = 'price', period: int = 20, std_dev: int = 2) -> pd.DataFrame:
    """
    Calculate Bollinger Bands
    Middle Band: 20-day SMA
    Upper Band: Middle + (2 * std deviation)
    Lower Band: Middle - (2 * std deviation)
    """
    df['bb_middle'] = df[price_col].rolling(window=period).mean()
    df['bb_std'] = df[price_col].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (std_dev * df['bb_std'])
    df['bb_lower'] = df['bb_middle'] - (std_dev * df['bb_std'])
    
    # Calculate %B (position within bands)
    df['bb_percent'] = (df[price_col] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    return df

def calculate_stochastic(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                         close_col: str = 'close', k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
    """
    Calculate Stochastic Oscillator
    %K = 100 * (Close - Lowest Low) / (Highest High - Lowest Low)
    %D = 3-period SMA of %K
    """
    lowest_low = df[low_col].rolling(window=k_period).min()
    highest_high = df[high_col].rolling(window=k_period).max()
    
    df['stoch_k'] = 100 * ((df[close_col] - lowest_low) / (highest_high - lowest_low))
    df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
    
    return df

def calculate_atr(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                  close_col: str = 'close', period: int = 14) -> pd.DataFrame:
    """
    Calculate Average True Range (ATR) - volatility indicator
    """
    high_low = df[high_col] - df[low_col]
    high_close = abs(df[high_col] - df[close_col].shift())
    low_close = abs(df[low_col] - df[close_col].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=period).mean()
    
    return df

def calculate_adx(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                  close_col: str = 'close', period: int = 14) -> pd.DataFrame:
    """
    Calculate Average Directional Index (ADX) - trend strength
    """
    # Calculate +DM and -DM
    high_diff = df[high_col].diff()
    low_diff = -df[low_col].diff()
    
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
    
    # Calculate ATR first
    df = calculate_atr(df, high_col, low_col, close_col, period)
    
    # Calculate +DI and -DI
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / df['atr'])
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / df['atr'])
    
    # Calculate DX and ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    df['adx'] = dx.rolling(window=period).mean()
    df['plus_di'] = plus_di
    df['minus_di'] = minus_di
    
    return df

def calculate_obv(df: pd.DataFrame, close_col: str = 'close', volume_col: str = 'volume') -> pd.DataFrame:
    """
    Calculate On-Balance Volume (OBV)
    """
    obv = [0]
    for i in range(1, len(df)):
        if df[close_col].iloc[i] > df[close_col].iloc[i-1]:
            obv.append(obv[-1] + df[volume_col].iloc[i])
        elif df[close_col].iloc[i] < df[close_col].iloc[i-1]:
            obv.append(obv[-1] - df[volume_col].iloc[i])
        else:
            obv.append(obv[-1])
    
    df['obv'] = obv
    return df

def calculate_vwap(df: pd.DataFrame, high_col: str = 'high', low_col: str = 'low', 
                   close_col: str = 'close', volume_col: str = 'volume') -> pd.DataFrame:
    """
    Calculate Volume Weighted Average Price (VWAP)
    """
    typical_price = (df[high_col] + df[low_col] + df[close_col]) / 3
    df['vwap'] = (typical_price * df[volume_col]).cumsum() / df[volume_col].cumsum()
    
    return df

def calculate_all_indicators(df: pd.DataFrame, price_col: str = 'close') -> pd.DataFrame:
    """
    Calculate all technical indicators at once
    For stocks: expects columns [open, high, low, close, volume]
    For gold: expects column [price_inr]
    """
    try:
        # Determine if this is stock data (has OHLCV) or simple price data
        has_ohlcv = all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
        
        if has_ohlcv:
            price_col = 'close'
        else:
            # For gold data, rename price_inr to close for consistency
            if 'price_inr' in df.columns:
                df['close'] = df['price_inr']
                price_col = 'close'
        
        # Moving Averages
        df = calculate_moving_averages(df, price_col)
        df = calculate_ema(df, price_col)
        
        # Oscillators
        df = calculate_rsi(df, price_col)
        df = calculate_macd(df, price_col)
        
        # Volatility
        df = calculate_bollinger_bands(df, price_col)
        
        # For stock data with OHLCV
        if has_ohlcv:
            df = calculate_stochastic(df)
            df = calculate_atr(df)
            df = calculate_adx(df)
            df = calculate_obv(df)
            df = calculate_vwap(df)
        
        # Returns and volatility
        df['returns'] = df[price_col].pct_change()
        df['log_returns'] = np.log(df[price_col] / df[price_col].shift(1))
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['volatility_annual'] = df['volatility'] * np.sqrt(252)  # Annualized
        
        logger.info(f"Calculated all indicators for {len(df)} data points")
        
        return df
        
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return df

def get_latest_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract latest indicator values as dictionary
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    indicators = {}
    
    # List of all indicator columns to extract
    indicator_cols = [
        'ma_5', 'ma_10', 'ma_20', 'ma_50', 'ma_100', 'ma_200',
        'ema_12', 'ema_26', 'ema_50',
        'rsi', 'macd', 'macd_signal', 'macd_histogram',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_percent',
        'stoch_k', 'stoch_d', 'atr', 'adx', 'plus_di', 'minus_di',
        'obv', 'vwap', 'volatility', 'volatility_annual'
    ]
    
    for col in indicator_cols:
        if col in df.columns and pd.notna(latest[col]):
            indicators[col] = float(latest[col])
    
    # Add price info
    if 'close' in df.columns:
        indicators['latest_price'] = float(latest['close'])
    elif 'price_inr' in df.columns:
        indicators['latest_price'] = float(latest['price_inr'])
    
    # Add recent returns
    if 'returns' in df.columns:
        indicators['recent_return_5d'] = float(df['returns'].tail(5).mean())
        indicators['recent_return_20d'] = float(df['returns'].tail(20).mean())
    
    # Add volume if available
    if 'volume' in df.columns and pd.notna(latest['volume']):
        indicators['volume'] = int(latest['volume'])
    
    return indicators

def generate_trading_signals(df: pd.DataFrame) -> Dict[str, str]:
    """
    Generate buy/sell/hold signals based on indicators
    """
    if df.empty or len(df) < 2:
        return {"signal": "INSUFFICIENT_DATA"}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = {}
    
    # RSI Signal
    if 'rsi' in df.columns and pd.notna(latest['rsi']):
        if latest['rsi'] < 30:
            signals['rsi'] = "BUY"  # Oversold
        elif latest['rsi'] > 70:
            signals['rsi'] = "SELL"  # Overbought
        else:
            signals['rsi'] = "HOLD"
    
    # MACD Signal
    if all(col in df.columns for col in ['macd', 'macd_signal']):
        if pd.notna(latest['macd']) and pd.notna(prev['macd']):
            # Bullish crossover
            if latest['macd'] > latest['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                signals['macd'] = "BUY"
            # Bearish crossover
            elif latest['macd'] < latest['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                signals['macd'] = "SELL"
            else:
                signals['macd'] = "HOLD"
    
    # Moving Average Signal (Golden/Death Cross)
    if all(col in df.columns for col in ['ma_50', 'ma_200']):
        if pd.notna(latest['ma_50']) and pd.notna(latest['ma_200']):
            if latest['ma_50'] > latest['ma_200'] and prev['ma_50'] <= prev['ma_200']:
                signals['ma_cross'] = "BUY"  # Golden cross
            elif latest['ma_50'] < latest['ma_200'] and prev['ma_50'] >= prev['ma_200']:
                signals['ma_cross'] = "SELL"  # Death cross
            else:
                signals['ma_cross'] = "HOLD"
    
    # Bollinger Bands Signal
    if all(col in df.columns for col in ['bb_upper', 'bb_lower', 'close']):
        price = latest['close'] if 'close' in df.columns else latest.get('price_inr')
        if pd.notna(price) and pd.notna(latest['bb_upper']) and pd.notna(latest['bb_lower']):
            if price < latest['bb_lower']:
                signals['bollinger'] = "BUY"  # Below lower band
            elif price > latest['bb_upper']:
                signals['bollinger'] = "SELL"  # Above upper band
            else:
                signals['bollinger'] = "HOLD"
    
    # Aggregate signal
    buy_count = sum(1 for s in signals.values() if s == "BUY")
    sell_count = sum(1 for s in signals.values() if s == "SELL")
    
    if buy_count > sell_count and buy_count >= 2:
        signals['aggregate'] = "STRONG_BUY" if buy_count >= 3 else "BUY"
    elif sell_count > buy_count and sell_count >= 2:
        signals['aggregate'] = "STRONG_SELL" if sell_count >= 3 else "SELL"
    else:
        signals['aggregate'] = "HOLD"
    
    return signals
