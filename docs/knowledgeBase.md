Here's a detailed prompt to evaluate our current crypto trading approach:

```text
Please evaluate this cryptocurrency trading bot architecture and provide insights on potential improvements:

Current Architecture:
1. Market Data Integration:
   - Fetches real-time data for BTC/USDT and ETH/USDT pairs
   - Updates every 5 minutes
   - Monitors key indicators: price, volume, RSI, SMA

2. Dual AI Analysis System:
   - Uses both GPT-3.5 and Claude for market analysis
   - Each AI provides:
     * Trading direction (BUY/SELL/HOLD)
     * Confidence score (0-100)
     * Stop loss recommendation
     * Take profit targets
     * Risk assessment (1-10)
   - Requires both AIs to agree for trade execution
   - Minimum confidence threshold: 75%

3. Risk Management:
   - Base trade amount: $5
   - Maximum concurrent trades: 3
   - Daily loss limit: $100
   - Stop loss: 1%
   - Take profit: 1.5%
   - Maximum safety orders: 2

4. 3Commas Integration:
   - Automated trade execution
   - Uses DCA strategy with safety orders
   - Handles order management and position tracking

Questions for Analysis:
1. What are potential weaknesses in this dual AI approach?
2. How could the risk management parameters be optimized?
3. Are the update intervals and trading pairs appropriate?
4. What additional indicators or data sources could improve decision-making?
5. How could the system better handle market volatility?
6. What backtesting approaches would you recommend?
7. How can we improve the AI prompt engineering for better analysis?
8. What fail-safes should be added to prevent catastrophic losses?

Please provide a comprehensive analysis with specific recommendations for improvement.
```

