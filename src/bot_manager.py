from py3cw.request import Py3CW
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from config.config import Config

class BaseBotManager:
    """Base class for bot management"""
    def __init__(self):
        self.active_bots: Dict[str, int] = {}  # pair -> bot_id mapping
        self.deal_history: List[Dict] = []

    async def create_bot(self, pair: str) -> Optional[Dict]:
        """Create a new bot for a trading pair"""
        raise NotImplementedError

    async def apply_ai_recommendations(self, bot_id: int, recommendations: Dict[str, Any]) -> bool:
        """Apply AI trading recommendations to bot settings"""
        raise NotImplementedError

    async def get_bot_stats(self, bot_id: int) -> Optional[Dict]:
        """Get bot performance statistics"""
        raise NotImplementedError

class MockBotManager(BaseBotManager):
    """Mock implementation for testing"""
    def __init__(self):
        super().__init__()
        self.mock_trades = {}
        self.next_bot_id = 1000
        logging.info("Creating MockBotManager for testing/development")

    async def create_bot(self, pair: str) -> Optional[Dict]:
        """Create a mock bot"""
        bot_id = self.next_bot_id
        self.next_bot_id += 1
        self.active_bots[pair] = bot_id
        return {'id': bot_id, 'pair': pair}

    async def apply_ai_recommendations(self, bot_id: int, recommendations: Dict[str, Any]) -> bool:
        """Mock implementation of applying AI recommendations"""
        try:
            # Store the recommendations for the bot
            if bot_id not in self.mock_trades:
                self.mock_trades[bot_id] = []
                
            self.mock_trades[bot_id].append({
                'timestamp': recommendations.get('timestamp'),
                'price': recommendations.get('price'),
                'direction': recommendations.get('direction'),
                'confidence': recommendations.get('confidence'),
                'should_trade': recommendations.get('should_trade', False)
            })
            
            logging.info(f"Mock bot {bot_id} applied recommendations: {recommendations}")
            return True
            
        except Exception as e:
            logging.error(f"Error in mock apply_ai_recommendations: {str(e)}")
            return False

    async def get_bot_stats(self, bot_id: int) -> Optional[Dict]:
        """Get mock bot statistics"""
        trades = self.mock_trades.get(bot_id, [])
        return {
            'profit': '0.00%',  # Mock profit
            'total_trades': len(trades),
            'last_trade': trades[-1] if trades else None
        }

class RealBotManager(BaseBotManager):
    """Real implementation using 3Commas API"""
    def __init__(self):
        super().__init__()
        self.p3cw = Py3CW(
            key=Config.THREE_COMMAS_API_KEY,
            secret=Config.THREE_COMMAS_SECRET,
            request_options={
                'request_timeout': 30,
                'nr_of_retries': 3
            }
        )

    # Your existing implementation methods here
    async def create_bot(self, pair: str) -> Optional[Dict]:
        """Create a new DCA bot for a trading pair"""
        try:
            # Get account info first
            account = await self.get_account_info()
            if not account:
                return None
                
            # Create bot with account ID
            error, bot = self.p3cw.request(
                entity='bots',
                action='create_bot',
                payload={
                    'name': f'AI_Bot_{pair}_{datetime.now().strftime("%Y%m%d")}',
                    'account_id': account['id'],
                    'pairs': pair,
                    'base_order_volume': Config.BASE_TRADE_AMOUNT,
                    'take_profit': Config.TAKE_PROFIT_PERCENTAGE,
                    'safety_order_volume': Config.BASE_TRADE_AMOUNT,
                    'martingale_volume_coefficient': 1.5,
                    'martingale_step_coefficient': 1.0,
                    'max_safety_orders': Config.MAX_SAFETY_ORDERS,
                    'active_safety_orders_count': Config.MAX_SAFETY_ORDERS,
                    'safety_order_step_percentage': 2.5,
                    'take_profit_type': 'total',
                    'strategy_list': [{'strategy': 'nonstop'}],
                    'min_volume_btc_24h': 0,
                    'profit_currency': 'quote_currency',
                    'start_order_type': 'limit',
                    'stop_loss_percentage': Config.STOP_LOSS_PERCENTAGE,
                    'cooldown': 1
                }
            )
            
            if error:
                logging.error(f"Error creating bot: {error}")
                return None
                
            self.active_bots[pair] = bot['id']
            logging.info(f"Created bot for {pair} with ID: {bot['id']}")
            return bot
            
        except Exception as e:
            logging.error(f"Error in create_bot: {str(e)}")
            return None

    async def apply_ai_recommendations(self, bot_id: int, recommendations: Dict[str, Any]) -> bool:
        """Apply AI trading recommendations to bot settings"""
        try:
            if not recommendations.get('should_trade', False):
                logging.info(f"Skipping bot update - AI doesn't recommend trading")
                return False
                
            # Extract recommendations
            take_profit = recommendations.get('take_profit')
            stop_loss = recommendations.get('stop_loss')
            
            if not take_profit or not stop_loss:
                logging.error("Missing take profit or stop loss recommendations")
                return False
                
            # Update bot settings
            new_settings = {
                'take_profit': take_profit,
                'stop_loss_percentage': stop_loss,
                'max_safety_orders': (
                    Config.MAX_SAFETY_ORDERS 
                    if recommendations.get('average_confidence', 0) > 85 
                    else 1
                )
            }
            
            success = await self.update_bot_settings(bot_id, new_settings)
            if success:
                logging.info(
                    f"Applied AI recommendations to bot {bot_id}:"
                    f"\nTake Profit: {take_profit}%"
                    f"\nStop Loss: {stop_loss}%"
                    f"\nConfidence: {recommendations.get('average_confidence')}%"
                )
            return success
            
        except Exception as e:
            logging.error(f"Error in apply_ai_recommendations: {str(e)}")
            return False

    async def get_bot_stats(self, bot_id: int) -> Optional[Dict]:
        """Get bot performance statistics"""
        try:
            error, stats = self.p3cw.request(
                entity='bots',
                action='stats',
                action_id=str(bot_id)
            )
            
            if error:
                logging.error(f"Error getting bot stats: {error}")
                return None
                
            return stats
            
        except Exception as e:
            logging.error(f"Error in get_bot_stats: {str(e)}")
            return None

# Factory function to create appropriate bot manager
def create_bot_manager(mock_mode: bool = True) -> BaseBotManager:
    """Create either a mock or real bot manager based on mode"""
    return MockBotManager() if mock_mode else RealBotManager()