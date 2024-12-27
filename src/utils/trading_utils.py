from decimal import Decimal, ROUND_DOWN
from typing import Union

def calculate_position_size(
    account_size: float,
    risk_percentage: float,
    stop_loss_percentage: float
) -> float:
    """
    Calculate position size based on account risk management
    """
    risk_amount = account_size * (risk_percentage / 100)
    position_size = risk_amount / (stop_loss_percentage / 100)
    return round(position_size, 2)

def validate_price(price: Union[str, float, Decimal]) -> Decimal:
    """
    Validate and convert price to Decimal
    """
    try:
        price_decimal = Decimal(str(price))
        if price_decimal <= 0:
            raise ValueError("Price must be greater than 0")
        return price_decimal
    except Exception as e:
        raise ValueError(f"Invalid price value: {str(e)}")

def calculate_order_quantity(
    price: float,
    amount: float,
    decimals: int = 8
) -> Decimal:
    """
    Calculate order quantity based on price and amount
    """
    price_decimal = Decimal(str(price))
    amount_decimal = Decimal(str(amount))
    quantity = amount_decimal / price_decimal
    
    # Round down to avoid exceeding available funds
    return quantity.quantize(
        Decimal(f"0.{'0' * decimals}"),
        rounding=ROUND_DOWN
    )

def calculate_take_profit(
    entry_price: float,
    profit_percentage: float,
    side: str = 'buy'
) -> float:
    """
    Calculate take profit price
    """
    entry_decimal = Decimal(str(entry_price))
    percentage = Decimal(str(profit_percentage)) / Decimal('100')
    
    if side.lower() == 'buy':
        return float(entry_decimal * (Decimal('1') + percentage))
    return float(entry_decimal * (Decimal('1') - percentage))