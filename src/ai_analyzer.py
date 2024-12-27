import logging
from openai import AsyncOpenAI
from anthropic import Anthropic
from typing import Dict, Any, Optional
from config.config import Config

class AIAnalyzer:
    def __init__(self):
        """Initialize AI analyzer with API clients"""
        self.openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.claude_client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.last_analysis = {}

    def _parse_ai_response(self, response: str, source: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into structured format"""
        try:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            result = {}

            for line in lines:
                if ':' not in line:
                    continue

                key, value = [x.strip() for x in line.split(':', 1)]
                key = key.upper()

                if key == 'DECISION':
                    result['direction'] = value.upper()
                elif key == 'CONFIDENCE':
                    result['confidence'] = float(value.replace('%', ''))
                elif key == 'STOP_LOSS':
                    result['stop_loss'] = float(value.replace('%', ''))
                elif key == 'TAKE_PROFIT':
                    result['take_profit'] = float(value.replace('%', ''))
                elif key == 'RISK':
                    result['risk'] = int(value)

            result['source'] = source
            logging.info(f"Parsed {source} response: {result}")
            return result

        except Exception as e:
            logging.error(f"Error parsing {source} response: {str(e)}")
            return None

    def _format_number(self, value: Any, prefix: str = "") -> str:
        """Safely format number with optional prefix"""
        try:
            if value is None or value == 'N/A':
                return 'N/A'
            if isinstance(value, (int, float)):
                return f"{prefix}{value:,.2f}"
            return str(value)
        except:
            return str(value)

    def _create_analysis_prompt(self, market_data: Dict[str, Any]) -> str:
        """Create detailed prompt for AI analysis using live data"""
        try:
            # Safely format all numeric values
            price = self._format_number(market_data.get('current_price'), "$")
            change = self._format_number(market_data.get('price_change_24h'))
            volume = self._format_number(market_data.get('volume_24h'), "$")
            rsi = self._format_number(market_data.get('indicators', {}).get('rsi_14'))
            sma_diff = self._format_number(market_data.get('indicators', {}).get('price_vs_sma'))
            volatility = self._format_number(market_data.get('volatility'))

            prompt = f"""
            Analyze this crypto market data and provide trading recommendations:

            Current Market Data:
            - Price: {price} (LIVE)
            - 24h Change: {change}%
            - Volume: {volume}
            - Trend: {market_data.get('trend', 'N/A')}
            - RSI: {rsi}
            - Price vs SMA: {sma_diff}%
            - Volatility: {volatility}

            Last Analysis Direction: {self.last_analysis.get('recommended_direction', 'N/A')}
            Last Analysis Confidence: {self._format_number(self.last_analysis.get('average_confidence'))}%

            Provide trading recommendation in this exact format:
            DECISION: [BUY/SELL/HOLD]
            CONFIDENCE: [0-100]
            STOP_LOSS: [percentage]
            TAKE_PROFIT: [percentage]
            RISK: [1-10]
            """
            
            return prompt

        except Exception as e:
            logging.error(f"Error creating prompt: {str(e)}")
            # Return a basic prompt as fallback
            return """
            Analyze the market data and provide:
            DECISION: [BUY/SELL/HOLD]
            CONFIDENCE: [0-100]
            STOP_LOSS: [percentage]
            TAKE_PROFIT: [percentage]
            RISK: [1-10]
            """

    async def _get_gpt_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get analysis from GPT with live data"""
        try:
            logging.info("Requesting GPT analysis...")
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a crypto trading expert analyzing live market data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            logging.info("Received GPT response")
            return self._parse_ai_response(response.choices[0].message.content, 'gpt')
        except Exception as e:
            logging.error(f"GPT analysis error: {str(e)}")
            return None

    async def _get_claude_analysis(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get analysis from Claude with live data"""
        try:
            logging.info("Requesting Claude analysis...")
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response.content:
                logging.info("Received Claude response")
                return self._parse_ai_response(response.content[0].text, "claude")
            return None
        except Exception as e:
            logging.error(f"Claude analysis error: {str(e)}")
            return None

    async def analyze_market(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get analysis from both AIs using live market data"""
        try:
            current_price = market_data.get('current_price')
            logging.info(f"Starting market analysis with price: {self._format_number(current_price, '$')}")
            
            prompt = self._create_analysis_prompt(market_data)

            # Get analysis from both AIs
            gpt_analysis = await self._get_gpt_analysis(prompt)
            claude_analysis = await self._get_claude_analysis(prompt)

            if gpt_analysis and claude_analysis:
                analysis_result = {
                    'gpt_analysis': gpt_analysis,
                    'claude_analysis': claude_analysis,
                    'gpt_confidence': gpt_analysis.get('confidence', 0),
                    'claude_confidence': claude_analysis.get('confidence', 0),
                    'agreement': gpt_analysis.get('direction') == claude_analysis.get('direction'),
                    'recommended_direction': gpt_analysis.get('direction'),
                    'average_confidence': (gpt_analysis.get('confidence', 0) +
                                        claude_analysis.get('confidence', 0)) / 2,
                    'should_trade': (
                        gpt_analysis.get('direction') == claude_analysis.get('direction') and
                        (gpt_analysis.get('confidence', 0) + claude_analysis.get('confidence', 0)) / 2 >= Config.MIN_CONFIDENCE_THRESHOLD
                    ),
                    'timestamp': market_data.get('timestamp'),
                    'current_price': current_price
                }
                
                # Cache the analysis
                self.last_analysis = analysis_result
                
                logging.info(f"Analysis complete - Direction: {analysis_result['recommended_direction']}, "
                           f"Confidence: {analysis_result['average_confidence']}%, "
                           f"Agreement: {analysis_result['agreement']}")
                           
                return analysis_result
                
            return None
        except Exception as e:
            logging.error(f"Error in market analysis: {str(e)}")
            return None

    async def get_trading_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get trading signals based on latest analysis"""
        analysis = await self.analyze_market(market_data)
        if not analysis:
            return {
                'should_trade': False,
                'reason': 'Analysis failed',
                'price': market_data.get('current_price'),
                'timestamp': market_data.get('timestamp')
            }
            
        return {
            'should_trade': analysis['should_trade'],
            'direction': analysis['recommended_direction'],
            'confidence': analysis['average_confidence'],
            'stop_loss': analysis['gpt_analysis'].get('stop_loss', Config.STOP_LOSS_PERCENTAGE),
            'take_profit': analysis['gpt_analysis'].get('take_profit', Config.TAKE_PROFIT_PERCENTAGE),
            'agreement': analysis['agreement'],
            'price': market_data.get('current_price'),
            'timestamp': market_data.get('timestamp')
        }