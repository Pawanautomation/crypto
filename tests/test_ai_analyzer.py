import pytest
import logging
import asyncio
from datetime import datetime
from src.ai_analyzer import AIAnalyzer
from src.market_data import MarketDataManager
from config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
async def market_data():
    """Fixture for market data manager"""
    manager = None
    try:
        manager = MarketDataManager()
        await manager.start()
        yield manager
    finally:
        if manager:
            try:
                await manager.stop()
            except Exception as e:
                logger.error(f"Error stopping market data in fixture: {str(e)}")

@pytest.fixture(scope="function")
async def ai_analyzer():
    """Fixture for AI analyzer"""
    return AIAnalyzer()

@pytest.mark.asyncio
async def test_ai_analyzer_live_data(market_data, ai_analyzer):
    """Test AI analyzer with live market data"""
    try:
        # Get live market data
        btc_data = await market_data.get_market_data("BTCUSDT")
        logger.info(f"Received live market data: {btc_data}")
        
        # Verify market data structure
        assert btc_data is not None, "Market data should not be None"
        assert 'current_price' in btc_data, "Market data should include current price"
        assert btc_data['current_price'] > 0, "Current price should be positive"
        
        # Get AI analysis
        analysis = await ai_analyzer.analyze_market(btc_data)
        logger.info(f"AI Analysis result: {analysis}")
        
        # Verify analysis
        assert analysis is not None, "Analysis should not be None"
        assert 'current_price' in analysis, "Analysis should include current price"
        assert abs(analysis['current_price'] - btc_data['current_price']) < 100, "Analysis should use live price"
        assert 'recommended_direction' in analysis, "Analysis should include direction"
        assert 'average_confidence' in analysis, "Analysis should include confidence"
        assert isinstance(analysis['average_confidence'], (int, float)), "Confidence should be numeric"
        assert 0 <= analysis['average_confidence'] <= 100, "Confidence should be between 0 and 100"
        
        # Get trading signals
        signals = await ai_analyzer.get_trading_signals(btc_data)
        logger.info(f"Trading signals: {signals}")
        
        # Verify signals
        assert signals is not None, "Signals should not be None"
        assert 'price' in signals, "Signals should include price"
        assert abs(signals['price'] - btc_data['current_price']) < 100, "Signals should use live price"
        assert 'should_trade' in signals, "Signals should include trade decision"
        assert 'direction' in signals, "Signals should include direction"
        assert signals['direction'] in ['BUY', 'SELL', 'HOLD'], f"Invalid direction: {signals['direction']}"
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_ai_agreement_check(market_data, ai_analyzer):
    """Test AI agreement and confidence threshold"""
    try:
        # Get market data
        btc_data = await market_data.get_market_data("BTCUSDT")
        
        # Get analysis
        analysis = await ai_analyzer.analyze_market(btc_data)
        
        # Verify agreement logic
        if analysis['should_trade']:
            assert analysis['agreement'], "Should only trade when AIs agree"
            assert analysis['average_confidence'] >= Config.MIN_CONFIDENCE_THRESHOLD, \
                "Should only trade above confidence threshold"
            
        logger.info(
            f"Agreement test - Should Trade: {analysis['should_trade']}, "
            f"Agreement: {analysis['agreement']}, "
            f"Confidence: {analysis['average_confidence']}%"
        )
        
    except Exception as e:
        logger.error(f"Agreement test failed: {str(e)}")
        raise