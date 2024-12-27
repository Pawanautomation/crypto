import pytest
import logging
import asyncio
from src.websocket_manager import BinanceWebsocketManager
from src.market_data import MarketDataManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data received event
data_received = asyncio.Event()
price_data_store = {}

def price_callback(price_data: dict):
    """Test callback for price updates"""
    logger.info(f"Callback received price update for {price_data['symbol']}: {price_data['current_price']}")
    price_data_store.update(price_data)
    data_received.set()

@pytest.fixture(scope="function")
async def ws_manager():
    """Fixture for websocket manager"""
    manager = None
    try:
        manager = BinanceWebsocketManager()
        await manager.start()
        yield manager
    finally:
        if manager:
            try:
                await manager.stop()
            except Exception as e:
                logger.error(f"Error stopping manager in fixture: {str(e)}")

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

@pytest.mark.asyncio
async def test_websocket_connection(ws_manager):
    """Test websocket connection can be established"""
    try:
        assert ws_manager.is_running() == True
        await ws_manager.stop()
        assert ws_manager.is_running() == False
    except Exception as e:
        logger.error(f"Websocket connection test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_price_subscription(ws_manager):
    """Test price subscription and updates"""
    try:
        logger.info("Starting price subscription test")
        
        # Reset event and data store
        data_received.clear()
        price_data_store.clear()
        
        # Add callback
        ws_manager.add_callback(price_callback)
        logger.info("Added price callback")
        
        # Subscribe to symbol
        await ws_manager.subscribe_symbols(["BTCUSDT"])
        logger.info("Subscribed to BTCUSDT")
        
        # Wait for initial data with timeout
        try:
            logger.info("Waiting for price data...")
            await asyncio.wait_for(data_received.wait(), timeout=30.0)
            logger.info("Received price data successfully")
            
            # Verify price data
            price = ws_manager.get_latest_price("BTCUSDT")
            assert price is not None, "Price should not be None"
            assert price > 0, "Price should be greater than 0"
            assert isinstance(price, float), "Price should be a float"
            
            logger.info(f"Final price verification successful: {price}")
            
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for price update")
            pytest.fail("Timeout waiting for price update")
            
    except Exception as e:
        logger.error(f"Price subscription test failed: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_market_data_integration(market_data):
    """Test market data integration"""
    try:
        logger.info("Starting market data integration test")
        
        # Get market data
        btc_data = await market_data.get_market_data("BTCUSDT")
        logger.info(f"Received market data: {btc_data}")
        
        # Verify data structure
        assert btc_data is not None, "Market data should not be None"
        assert 'current_price' in btc_data, "Market data should include current_price"
        assert 'trend' in btc_data, "Market data should include trend"
        assert 'indicators' in btc_data, "Market data should include indicators"
        
        # Verify values
        assert isinstance(btc_data['current_price'], (int, float)), "Price should be numeric"
        assert btc_data['current_price'] > 0, "Price should be greater than 0"
        
        logger.info("Market data integration test completed successfully")
        
    except Exception as e:
        logger.error(f"Market data integration test failed: {str(e)}")
        raise