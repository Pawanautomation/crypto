from binance import Client
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from config.config import Config

class MarketDataManager:
    def __init__(self):
        # Initialize Binance client (we'll use it for market data only)
        self.client = Client("", "")  # No keys needed for public data
        self.cached_data = {}
        self.last_update = None
        
    async def get_market_data(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """
        Get current market data including price, volume, and indicators
        """
        try:
            current_time = datetime.now()
            
            # Check if cache is valid (less than 1 minute old)
            if (self.last_update and 
                current_time - self.last_update < timedelta(minutes=1) and
                symbol in self.cached_data):
                return self.cached_data[symbol]

            # Get current ticker data
            ticker = self.client.get_ticker(symbol=symbol)
            
            # Get recent klines (candlestick data)
            klines = self.client.get_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1HOUR,
                limit=24
            )
            
            # Calculate basic indicators
            market_data = {
                'symbol': symbol,
                'current_price': float(ticker['lastPrice']),
                'price_change_24h': float(ticker['priceChangePercent']),
                'volume_24h': float(ticker['volume']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'timestamp': current_time.isoformat(),
                'trend': self._calculate_trend(klines),
                'volatility': self._calculate_volatility(klines),
                'indicators': self._calculate_indicators(klines)
            }
            
            # Update cache
            self.cached_data[symbol] = market_data
            self.last_update = current_time
            
            return market_data
            
        except Exception as e:
            logging.error(f"Error fetching market data: {str(e)}")
            return None
    
    def _calculate_trend(self, klines: list) -> str:
        """
        Calculate current trend based on recent prices
        """
        if not klines or len(klines) < 2:
            return "neutral"
            
        recent_closes = [float(k[4]) for k in klines[-6:]]  # Last 6 hours
        first_price = recent_closes[0]
        last_price = recent_closes[-1]
        
        price_change = ((last_price - first_price) / first_price) * 100
        
        if price_change > 1:
            return "bullish"
        elif price_change < -1:
            return "bearish"
        return "neutral"
    
    def _calculate_volatility(self, klines: list) -> float:
        """
        Calculate recent volatility
        """
        if not klines or len(klines) < 2:
            return 0.0
            
        recent_prices = [float(k[4]) for k in klines[-12:]]  # Last 12 hours
        price_changes = [
            abs((recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] * 100)
            for i in range(1, len(recent_prices))
        ]
        
        return sum(price_changes) / len(price_changes)
    
    def _calculate_indicators(self, klines: list) -> Dict[str, float]:
        """
        Calculate basic technical indicators
        """
        if not klines or len(klines) < 14:  # Need at least 14 periods for RSI
            return {}
            
        closes = [float(k[4]) for k in klines]
        
        return {
            'sma_20': self._calculate_sma(closes, 20),
            'rsi_14': self._calculate_rsi(closes, 14),
            'price_vs_sma': (closes[-1] / self._calculate_sma(closes, 20) - 1) * 100
        }
    
    def _calculate_sma(self, prices: list, period: int) -> float:
        """
        Calculate Simple Moving Average
        """
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    def _calculate_rsi(self, prices: list, period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        """
        if len(prices) < period + 1:
            return 50.0
            
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # Calculate average gains and losses
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)

    async def get_historical_data(self, symbol: str = "BTCUSDT", 
                                days: int = 7) -> list:
        """
        Get historical price data
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1HOUR,
                start_str=start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_str=end_time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return [{
                'timestamp': datetime.fromtimestamp(k[0] / 1000).isoformat(),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in klines]
            
        except Exception as e:
            logging.error(f"Error fetching historical data: {str(e)}")
            return []