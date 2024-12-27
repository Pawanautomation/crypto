import pytest
import asyncio
import logging
from src.bot_manager import create_bot_manager
from config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
async def mock_bot_manager():
    """Fixture for mock bot manager"""
    return create_bot_manager(use_mock=True)

@pytest.mark.asyncio
async def test_mock_bot_creation(mock_bot_manager):
    """Test creating a mock bot"""
    # Create a test bot
    bot = await mock_bot_manager.create_bot("BTCUSDT")
    
    # Verify bot creation
    assert bot is not None
    assert 'id' in bot
    assert bot['pair'] == "BTCUSDT"
    assert bot['status'] == 'enabled'
    
    # Test bot operations
    bot_id = bot['id']
    
    # Test updating settings
    success = await mock_bot_manager.update_bot_settings(
        bot_id,
        {'take_profit': 2.0, 'stop_loss': 1.5}
    )
    assert success is True
    
    # Test simulating a trade
    deal = await mock_bot_manager.simulate_trade(bot_id, 50000.0, 'buy')
    assert deal is not None
    assert deal['bot_id'] == bot_id
    assert deal['type'] == 'buy'
    
    # Test getting deals
    deals = await mock_bot_manager.get_bot_deals(bot_id)
    assert len(deals) > 0
    assert deals[0]['bot_id'] == bot_id
    
    # Test stopping bot
    success = await mock_bot_manager.stop_bot(bot_id)
    assert success is True

if __name__ == "__main__":
    pytest.main([__file__, '-v'])