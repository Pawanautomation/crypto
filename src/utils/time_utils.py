from datetime import datetime, timezone
from typing import Union

def get_timestamp(ms: bool = False) -> Union[int, float]:
    """
    Get current UTC timestamp
    """
    now = datetime.now(timezone.utc)
    if ms:
        return int(now.timestamp() * 1000)
    return int(now.timestamp())

def format_time(timestamp: Union[int, float], format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp to readable string
    """
    # Convert milliseconds to seconds if necessary
    if timestamp > 1e11:  # Assume milliseconds if timestamp is too large
        timestamp = timestamp / 1000
        
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    return dt.strftime(format_string)

def get_time_diff(timestamp1: Union[int, float], timestamp2: Union[int, float]) -> float:
    """
    Get time difference in seconds between two timestamps
    """
    # Convert both timestamps to seconds if in milliseconds
    if timestamp1 > 1e11:
        timestamp1 = timestamp1 / 1000
    if timestamp2 > 1e11:
        timestamp2 = timestamp2 / 1000
        
    return abs(timestamp1 - timestamp2)

def is_market_active(timestamp: Union[int, float] = None) -> bool:
    """
    Check if current time is within trading hours
    Crypto markets are 24/7, but you might want to limit trading times
    """
    if timestamp is None:
        timestamp = get_timestamp()
        
    # Convert timestamp to datetime
    dt = datetime.fromtimestamp(timestamp, timezone.utc)
    
    # Example: Only trade between 00:00 and 23:00 UTC
    return dt.hour < 23