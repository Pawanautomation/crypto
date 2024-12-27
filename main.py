import os
import logging
import asyncio
from typing import Union
from datetime import datetime
from src.market_data import MarketDataManager
from src.ai_analyzer import AIAnalyzer
from src.bot_manager import RealBotManager, MockBotManager, create_bot_manager
from config.config import Config

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

class TradingBot:
    def __init__(self, mock_mode: bool = True):
        """Initialize trading bot with optional mock mode"""
        self.market_data = MarketDataManager()
        self.ai_analyzer = AIAnalyzer()
        self.bot_manager = create_bot_manager(mock_mode)
        self.is_running = False
        self.mock_mode = mock_mode
        
        if mock_mode:
            logger.info("Running in mock mode - no real trades will be executed")
            
    async def setup(self):
        """Initialize the trading system"""
        try:
            # Start market data services
            await self.market_data.start()
            
            # Validate configuration
            Config.validate_config()
            print("\nValidating Configuration:")
            print(f"Mock Mode: {'Enabled' if self.mock_mode else 'Disabled'}")
            
            # Create initial bot for each trading pair
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
        
        while self.is_running:
            try:
                for pair in Config.TRADING_PAIRS:
                    await self.process_trading_pair(pair)
                    
                # Wait for next update interval
                await asyncio.sleep(Config.UPDATE_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def process_trading_pair(self, pair: str):
        """Process a single trading pair"""
        try:
            # Get market data
            market_data = await self.market_data.get_market_data(pair)
            if not market_data:
                logger.warning(f"No market data available for {pair}")
                return
                
            # Get AI analysis
            analysis = await self.ai_analyzer.analyze_market(market_data)
            if not analysis:
                logger.warning(f"No AI analysis available for {pair}")
                return
                
            # Get bot ID for this pair
            bot_id = self.bot_manager.active_bots.get(pair)
            if not bot_id:
                logger.warning(f"No active bot found for {pair}")
                return
                
            # Apply AI recommendations
            success = await self.bot_manager.apply_ai_recommendations(
                bot_id, analysis
            )
            
            if success:
                logger.info(f"Successfully updated bot settings for {pair}")
                
            # Log current status
            await self.log_status(pair, market_data, analysis)
            
        except Exception as e:
            logger.error(f"Error processing {pair}: {str(e)}")
    
    async def log_status(self, pair: str, market_data: dict, analysis: dict):
        """Log current trading status"""
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
        # Clean up market data services
        await self.market_data.stop()

async def main():
    """Main entry point"""
    bot = TradingBot(mock_mode=True)  # Set to False for real trading
    
    try:
        # Initialize the bot
        await bot.setup()
        
        # Run the main loop
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await bot.stop()
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        await bot.stop()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.critical(f"Application crashed: {str(e)}")