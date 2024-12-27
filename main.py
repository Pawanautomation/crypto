from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import asyncio
from typing import Union, Dict, Any
from datetime import datetime
from src.market_data import MarketDataManager
from src.ai_analyzer import AIAnalyzer
from src.bot_manager import RealBotManager, MockBotManager, create_bot_manager
from config.config import Config
from starlette.websockets import WebSocketDisconnect

# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
   level=logging.INFO,
   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
   handlers=[
       logging.FileHandler('logs/trading.log'),
       logging.StreamHandler()
   ]
)

logger = logging.getLogger('TradingBot')

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:3000"],
   allow_credentials=True, 
   allow_methods=["*"],
   allow_headers=["*"],
)

class TradingBot:
   def __init__(self, mock_mode: bool = True):
       self.market_data = MarketDataManager()
       self.ai_analyzer = AIAnalyzer()
       self.bot_manager = create_bot_manager(mock_mode)
       self.is_running = False
       self.mock_mode = mock_mode
       self.market_data_task = None
       
       if mock_mode:
           logger.info("Running in mock mode - no real trades will be executed")
           
   async def setup(self):
       try:
           await self.market_data.start()
           Config.validate_config()
           print("\nValidating Configuration:")
           print(f"Mock Mode: {'Enabled' if self.mock_mode else 'Disabled'}")
           
           for pair in Config.TRADING_PAIRS:
               bot = await self.bot_manager.create_bot(pair)
               if bot:
                   logger.info(f"Created bot for {pair}: {bot['id']}")
               else:
                   logger.error(f"Failed to create bot for {pair}")
                   
       except Exception as e:
           logger.error(f"Setup failed: {str(e)}")
           raise

   async def run(self):
       """Main trading loop"""
       self.is_running = True
       logger.info("Starting trading bot...")
       
       try:
           while self.is_running:
               for pair in Config.TRADING_PAIRS:
                   await self.process_trading_pair(pair)
               await asyncio.sleep(Config.UPDATE_INTERVAL)
       except Exception as e:
           logger.error(f"Error in main loop: {str(e)}")
           
   async def process_trading_pair(self, pair: str):
       """Process a single trading pair"""
       try:
           market_data = await self.market_data.get_market_data(pair)
           if not market_data:
               logger.warning(f"No market data available for {pair}")
               return

           analysis = await self.ai_analyzer.analyze_market(market_data)
           if not analysis:
               logger.warning(f"No AI analysis available for {pair}")
               return
               
           bot_id = self.bot_manager.active_bots.get(pair)
           if not bot_id:
               logger.warning(f"No active bot found for {pair}")
               return
               
           success = await self.bot_manager.apply_ai_recommendations(
               bot_id, analysis
           )
           
           if success:
               logger.info(f"Successfully updated bot settings for {pair}")
               await self.log_status(pair, market_data, analysis)
               
       except Exception as e:
           logger.error(f"Error processing {pair}: {str(e)}")
   
   async def log_status(self, pair: str, market_data: dict, analysis: dict):
       try:
           bot_id = self.bot_manager.active_bots.get(pair)
           if bot_id:
               stats = await self.bot_manager.get_bot_stats(bot_id)
               
               logger.info(
                   f"\nStatus Update for {pair}:"
                   f"\nCurrent Price: ${market_data['current_price']}"
                   f"\n24h Change: {market_data.get('price_change_24h', 'N/A')}%"
                   f"\nBot Performance: {stats.get('profit', 'Unknown')}"
                   f"\nAI Confidence: {analysis.get('average_confidence', 'Unknown')}%"
               )
               
       except Exception as e:
           logger.error(f"Error logging status: {str(e)}")
   
   async def stop(self):
       """Stop the trading bot"""
       self.is_running = False
       logger.info("Stopping trading bot...")
       await self.market_data.stop()
       if self.market_data_task:
           self.market_data_task.cancel()

# Initialize bot instance
bot = TradingBot(mock_mode=True)

async def start_bot():
   """Start the trading bot"""
   await bot.setup()
   bot.market_data_task = asyncio.create_task(bot.run())

@app.on_event("startup")
async def startup_event():
   await start_bot()

@app.get("/api/market-data")
async def get_market_data():
   try:
       market_data = await bot.market_data.get_market_data("BTCUSDT")
       if market_data:
           return market_data
       return {"error": "No market data available"}
   except Exception as e:
       logger.error(f"Error in market data endpoint: {str(e)}")
       return {"error": str(e)}

@app.get("/api/ai-analysis")
async def get_ai_analysis():
   try:
       market_data = await bot.market_data.get_market_data("BTCUSDT")
       if market_data:
           analysis = await bot.ai_analyzer.analyze_market(market_data)
           return analysis or {"error": "No analysis available"}
       return {"error": "No market data available"}
   except Exception as e:
       logger.error(f"Error in analysis endpoint: {str(e)}")
       return {"error": str(e)}

@app.websocket("/ws/market-data")
async def websocket_endpoint(websocket: WebSocket):
   await websocket.accept()
   
   try:
       while True:
           market_data = await bot.market_data.get_market_data("BTCUSDT")
           if market_data:
               await websocket.send_json({
                   'current_price': market_data['current_price'],
                   'price_change_24h': market_data.get('price_change_24h', 0),
                   'pair': "BTCUSDT",
                   'timestamp': datetime.now().isoformat()
               })
           await asyncio.sleep(5)
   except WebSocketDisconnect:
       logger.info("WebSocket client disconnected")
   except Exception as e:
       logger.error(f"WebSocket error: {str(e)}")
   finally:
       try:
           await websocket.close()
       except:
           pass

if __name__ == "__main__":
   try:
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)
   except KeyboardInterrupt:
       logger.info("Application terminated by user")
   except Exception as e:
       logger.critical(f"Application crashed: {str(e)}")