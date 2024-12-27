# service_test.py
import asyncio
import logging
from config.config import Config
from src.market_data import MarketDataManager
from src.ai_analyzer import AIAnalyzer
from src.bot_manager import BotManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openai():
    """Test OpenAI API connection"""
    try:
        analyzer = AIAnalyzer()
        test_data = {
            'current_price': 50000,
            'price_change_24h': 2.5,
            'volume_24h': 1000000000,
            'trend': 'bullish',
            'indicators': {
                'rsi_14': 55,
                'price_vs_sma': 1.2
            }
        }
        
        prompt = analyzer._create_analysis_prompt(test_data)
        gpt_response = await analyzer._get_gpt_analysis(prompt)
        
        if gpt_response:
            logger.info("OpenAI Test: ✓ Success")
            logger.info(f"Response: {gpt_response}")
            return True
        return False
    except Exception as e:
        logger.error(f"OpenAI Test Error: {str(e)}")
        return False

async def test_claude():
    """Test Claude API connection"""
    try:
        analyzer = AIAnalyzer()
        test_data = {
            'current_price': 50000,
            'price_change_24h': 2.5,
            'volume_24h': 1000000000,
            'trend': 'bullish',
            'indicators': {
                'rsi_14': 55,
                'price_vs_sma': 1.2
            }
        }
        
        prompt = analyzer._create_analysis_prompt(test_data)
        claude_response = await analyzer._get_claude_analysis(prompt)
        
        if claude_response:
            logger.info("Claude Test: ✓ Success")
            logger.info(f"Response: {claude_response}")
            return True
        return False
    except Exception as e:
        logger.error(f"Claude Test Error: {str(e)}")
        return False

async def test_3commas():
    """Test 3Commas API connection"""
    try:
        bot_manager = BotManager()
        is_valid = await bot_manager.verify_credentials()
        
        if is_valid:
            logger.info("3Commas Test: ✓ Success")
            return True
        return False
    except Exception as e:
        logger.error(f"3Commas Test Error: {str(e)}")
        return False

async def main():
    print("\nTesting Each Service Independently:")
    
    print("\n1. Testing OpenAI Connection:")
    openai_success = await test_openai()
    print(f"OpenAI Test: {'✓ Passed' if openai_success else '✗ Failed'}")
    
    print("\n2. Testing Claude Connection:")
    claude_success = await test_claude()
    print(f"Claude Test: {'✓ Passed' if claude_success else '✗ Failed'}")
    
    print("\n3. Testing 3Commas Connection:")
    threec_success = await test_3commas()
    print(f"3Commas Test: {'✓ Passed' if threec_success else '✗ Failed'}")

if __name__ == "__main__":
    asyncio.run(main())