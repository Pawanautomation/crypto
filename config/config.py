import os
from dotenv import load_dotenv
from pathlib import Path

# Get project root directory and load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    # Environment Settings
    USE_MOCK_BOT = os.getenv('USE_MOCK_BOT', 'false').lower() == 'true'
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    THREE_COMMAS_API_KEY = os.getenv('THREE_COMMAS_API_KEY')
    THREE_COMMAS_SECRET = os.getenv('THREE_COMMAS_SECRET')

    # Trading Parameters
    BASE_TRADE_AMOUNT = 5  # $5 base trade
    MAX_CONCURRENT_TRADES = 3
    MAX_DAILY_LOSS = 100  # $100 max daily loss
    
    # Trading Pairs
    TRADING_PAIRS = ['BTCUSDT', 'ETHUSDT']  # Changed format for Binance
    
    # Time intervals
    UPDATE_INTERVAL = 300  # 5 minutes
    
    # Risk Management
    STOP_LOSS_PERCENTAGE = 1.0  # 1%
    TAKE_PROFIT_PERCENTAGE = 1.5  # 1.5%
    MAX_SAFETY_ORDERS = 2

    # AI Configuration
    MIN_CONFIDENCE_THRESHOLD = 75  # Minimum confidence for trade execution
    AI_AGREEMENT_REQUIRED = True   # Require both AIs to agree

    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        required_keys = []
        
        # Only validate API keys if not in mock mode
        if not cls.USE_MOCK_BOT:
            required_keys.extend([
                'OPENAI_API_KEY',
                'CLAUDE_API_KEY',
                'THREE_COMMAS_API_KEY',
                'THREE_COMMAS_SECRET'
            ])
        
        print("\nValidating Configuration:")
        print(f"Mock Mode: {'Enabled' if cls.USE_MOCK_BOT else 'Disabled'}")
        
        for key in required_keys:
            value = getattr(cls, key)
            print(f"{key}: {'✓ Present' if value else '✗ Missing'}")
            if value:
                print(f"Length: {len(value)} characters")
        
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys and not cls.USE_MOCK_BOT:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True

    @classmethod
    def get_trading_parameters(cls):
        """Get all trading parameters in a dictionary"""
        return {
            'base_trade_amount': cls.BASE_TRADE_AMOUNT,
            'max_concurrent_trades': cls.MAX_CONCURRENT_TRADES,
            'max_daily_loss': cls.MAX_DAILY_LOSS,
            'stop_loss_percentage': cls.STOP_LOSS_PERCENTAGE,
            'take_profit_percentage': cls.TAKE_PROFIT_PERCENTAGE,
            'max_safety_orders': cls.MAX_SAFETY_ORDERS
        }