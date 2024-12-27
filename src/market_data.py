from binance import AsyncClient, Client
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from config.config import Config

class MarketDataManager:
    def __init__(self):
        """Initialize market data manager"""
        self.binance_client = Client("", "")  # Public client for market data
        self.cached_data = {}
        
    async def start(self):
        """Start market data services"""
        try:
            # Initialize the async client
            self.binance_client = await AsyncClient.create()
            logging.info("Market data services started")
        except Exception as e:
            logging.error(f"Error starting market data services: {str(e)}")
            raise

    async def stop(self):
        """Stop market data services"""
        try:
            if self.binance_client:
                await self.binance_client.close_connection()
            logging.info("Market data services stopped")
        except Exception as e:
            logging.error(f"Error stopping market data services: {str(e)}")
            raise

    async def get_market_data(self, symbol: str = "BTCUSDT") -> Optional[Dict[str, Any]]:
        """Get current market data including price, volume, and indicators"""
        try:
            # Get current ticker data
            ticker = await self.binance_client.get_ticker(symbol=symbol)
            
            # Get candlestick data for technical analysis
            klines = await self.binance_client.get_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1HOUR,
                limit=24
            )
            
            current_price = float(ticker['lastPrice'])
            
            market_data = {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_24h': float(ticker['priceChangePercent']),
                'volume_24h': float(ticker['volume']),
                'timestamp': datetime.now().isoformat(),
                'trend': self._calculate_trend(klines),
                'volatility': self._calculate_volatility(klines),
                'indicators': self._calculate_indicators(klines),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice'])
            }
            
            self.cached_data[symbol] = market_data
            return market_data
            
        except Exception as e:
            logging.error(f"Error fetching market data: {str(e)}")
            # Return cached data if available
            return self.cached_data.get(symbol)
            
    def _calculate_trend(self, klines: list) -> str:
        """Calculate current trend based on recent prices"""
        if not klines or len(klines) < 2:
            return "neutral"
            
        recent_closes = [float(k[4]) for k in klines[-6:]]
        first_price = recent_closes[0]
        last_price = recent_closes[-1]
        
        price_change = ((last_price - first_price) / first_price) * 100
        
        if price_change > 1:
            return "bullish"
        elif price_change < -1:
            return "bearish"
        return "neutral"
            
    def _calculate_volatility(self, klines: list) -> float:
        """Calculate recent volatility"""
        if not klines or len(klines) < 2:
            return 0.0
            
        recent_prices = [float(k[4]) for k in klines[-12:]]
        price_changes = [
            abs((recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] * 100)
            for i in range(1, len(recent_prices))
        ]
        
        return sum(price_changes) / len(price_changes)
            
    def _calculate_indicators(self, klines: list) -> Dict[str, float]:
        """Calculate technical indicators"""
        if not klines or len(klines) < 14:
            return {
                'sma_20': 0.0,
                'rsi_14': 50.0,
                'price_vs_sma': 0.0
            }
            
        closes = [float(k[4]) for k in klines]
        
        return {
            'sma_20': self._calculate_sma(closes, 20),
            'rsi_14': self._calculate_rsi(closes, 14),
            'price_vs_sma': (closes[-1] / self._calculate_sma(closes, 20) - 1) * 100
        }
            
    def _calculate_sma(self, prices: list, period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        return sum(prices[-period:]) / period
            
    def _calculate_rsi(self, prices: list, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
            
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)