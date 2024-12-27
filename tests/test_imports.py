import sys
from pathlib import Path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from config.config import Config
from src.market_data import MarketDataManager
from src.websocket_manager import BinanceWebsocketManager
from src.ai_analyzer import AIAnalyzer
from src.bot_manager import create_bot_manager

print("Config:", Config.USE_MOCK_BOT)
print("All imports successful!")