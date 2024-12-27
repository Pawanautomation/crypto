import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { ArrowUpCircle, ArrowDownCircle, AlertCircle, Percent, DollarSign, TrendingUp } from 'lucide-react';

const TradingOverview = () => {
  const [tradingData, setTradingData] = useState({
    pair: "BTC/USDT",
    currentPrice: 0,
    priceChange24h: 0,
    confidence: 0,
    aiRecommendation: "HOLD",
    riskLevel: 0,
    indicators: {}
  });

  const [priceHistory, setPriceHistory] = useState([]);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Fetch market data
        const response = await fetch('/api/market-data');
        const marketData = await response.json();
        
        // Update trading data with live values
        setTradingData(prev => ({
          ...prev,
          currentPrice: marketData.current_price,
          priceChange24h: marketData.price_change_24h,
          indicators: marketData.indicators
        }));

        // Fetch AI analysis
        const aiResponse = await fetch('/api/ai-analysis');
        const aiData = await aiResponse.json();
        
        setTradingData(prev => ({
          ...prev,
          confidence: aiData.average_confidence,
          aiRecommendation: aiData.recommended_direction,
          riskLevel: Math.max(aiData.gpt_analysis?.risk || 0, aiData.claude_analysis?.risk || 0)
        }));
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    // Set up WebSocket connection for live updates
    const ws = new WebSocket('ws://localhost:8000/ws/market-data');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTradingData(prev => ({
        ...prev,
        currentPrice: data.current_price,
        priceChange24h: data.price_change_24h
      }));

      // Add new price point to history
      setPriceHistory(prev => [
        ...prev,
        {
          time: new Date().toLocaleTimeString(),
          price: data.current_price
        }
      ].slice(-20)); // Keep last 20 points
    };

    fetchInitialData();

    return () => {
      ws.close();
    };
  }, []);

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY': return 'text-green-500';
      case 'SELL': return 'text-red-500';
      default: return 'text-yellow-500';
    }
  };

  // Rest of the component remains the same
  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
      <div className="mx-auto max-w-6xl bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        {/* Trading Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <div className="flex items-center space-x-4">
            <DollarSign className="h-8 w-8 text-blue-500" />
            <div>
              <p className="text-sm text-gray-500">Current Price</p>
              <p className="text-2xl font-bold">${tradingData.currentPrice.toLocaleString()}</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Percent className="h-8 w-8 text-purple-500" />
            <div>
              <p className="text-sm text-gray-500">24h Change</p>
              <p className="text-2xl font-bold">
                {tradingData.priceChange24h > 0 ? '+' : ''}{tradingData.priceChange24h.toFixed(2)}%
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <TrendingUp className="h-8 w-8 text-green-500" />
            <div>
              <p className="text-sm text-gray-500">Trading Pair</p>
              <p className="text-2xl font-bold">{tradingData.pair}</p>
            </div>
          </div>
        </div>

        {/* Price Chart */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Price History</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Analysis */}
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">AI Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-4">
              {tradingData.aiRecommendation === 'BUY' ? (
                <ArrowUpCircle className="h-8 w-8 text-green-500" />
              ) : (
                <ArrowDownCircle className="h-8 w-8 text-red-500" />
              )}
              <div>
                <p className="text-sm text-gray-500">AI Recommendation</p>
                <p className={`text-2xl font-bold ${getSignalColor(tradingData.aiRecommendation)}`}>
                  {tradingData.aiRecommendation}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <AlertCircle className="h-8 w-8 text-orange-500" />
              <div>
                <p className="text-sm text-gray-500">Risk Level</p>
                <p className="text-2xl font-bold">{tradingData.riskLevel}/10</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <TrendingUp className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-sm text-gray-500">AI Confidence</p>
                <p className="text-2xl font-bold">{tradingData.confidence.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingOverview;