import logging
from typing import Dict, Any, Set, Optional, List
from datetime import datetime
from binance import AsyncClient
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from config.config import Config

class BinanceWebsocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.market_data: Dict[str, Dict[str, Any]] = {}
        self.price_callbacks = []
        self.is_running = False
        self.binance_client = None
        self.tasks: List[asyncio.Task] = []
        self.last_rest_price: Dict[str, float] = {}
        self.last_ws_update: Dict[str, datetime] = {}
        self.ws_connection = None
        self.subscribed_symbols = set()
        
    async def start(self):
        """Start the WebSocket manager"""
        if not self.is_running:
            try:
                self.is_running = True
                self.binance_client = await AsyncClient.create()
                
                # Start the market data collection task
                data_task = asyncio.create_task(self._collect_market_data())
                self.tasks.append(data_task)
                
                logging.info("WebSocket manager started successfully")
            except Exception as e:
                self.is_running = False
                logging.error(f"Failed to start WebSocket manager: {str(e)}")
                raise
    
    async def stop(self):
        """Stop the WebSocket manager"""
        try:
            self.is_running = False
            
            # Cancel all tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Close all WebSocket connections
            for connection in self.active_connections:
                try:
                    await connection.close()
                except Exception:
                    pass
            
            # Close Binance client
            if self.binance_client:
                await self.binance_client.close_connection()
                
            self.tasks.clear()
            self.active_connections.clear()
            logging.info("WebSocket manager stopped successfully")
            
        except Exception as e:
            logging.error(f"Error stopping WebSocket manager: {str(e)}")
            raise
    
    async def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest price for a symbol with fallback"""
        try:
            # Try to get from market data first
            if symbol in self.market_data and self.market_data[symbol]['current_price'] is not None:
                return float(self.market_data[symbol]['current_price'])
            
            # Fallback to REST API
            if self.binance_client:
                ticker = await self.binance_client.get_ticker(symbol=symbol)
                price = float(ticker['lastPrice'])
                
                # Update market data
                if symbol in self.market_data:
                    self.market_data[symbol]['current_price'] = price
                
                return price
                
            return None
        except Exception as e:
            logging.error(f"Error getting latest price for {symbol}: {str(e)}")
            return None

    async def subscribe_symbols(self, symbols: List[str]):
        """Subscribe to market data for specified symbols"""
        try:
            for symbol in symbols:
                if symbol not in self.subscribed_symbols:
                    self.subscribed_symbols.add(symbol)
                    self.market_data[symbol] = {
                        'symbol': symbol,
                        'current_price': None,
                        'timestamp': None
                    }
            logging.info(f"Subscribed to symbols: {symbols}")
        except Exception as e:
            logging.error(f"Error subscribing to symbols: {str(e)}")

    async def _collect_market_data(self):
        """Collect market data for subscribed symbols"""
        while self.is_running:
            try:
                for symbol in self.subscribed_symbols:
                    # Get ticker data
                    ticker = await self.binance_client.get_ticker(symbol=symbol)
                    
                    # Update market data
                    self.market_data[symbol] = {
                        'symbol': symbol,
                        'current_price': float(ticker['lastPrice']),
                        'price_change_24h': float(ticker['priceChangePercent']),
                        'volume_24h': float(ticker['volume']),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Update last update time
                    self.last_ws_update[symbol] = datetime.now()
                    
                    # Notify callbacks
                    for callback in self.price_callbacks:
                        try:
                            callback(self.market_data[symbol])
                        except Exception as e:
                            logging.error(f"Error in price callback: {str(e)}")
                    
                    # Broadcast update
                    await self.broadcast(self.market_data[symbol])
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                logging.error(f"Error collecting market data: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def connect(self, websocket: WebSocket):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logging.error(f"WebSocket error: {str(e)}")
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logging.error(f"Error broadcasting to client: {str(e)}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected

    def add_price_callback(self, callback):
        """Add callback for price updates"""
        if callback not in self.price_callbacks:
            self.price_callbacks.append(callback)

    def remove_price_callback(self, callback):
        """Remove price callback"""
        if callback in self.price_callbacks:
            self.price_callbacks.remove(callback)