import requests
import logging
from ..config import BASE_API_URL, MARKET_DATA_FIELDS, PRICE_ADJUSTMENT_PERCENT

logger = logging.getLogger(__name__)

class MarketDataService:
    @staticmethod
    def get_live_market_data(conids):
        """Get live market data for specified conids"""
        try:
            url = f"{BASE_API_URL}/iserver/marketdata/snapshot"
            params = {
                'conids': ','.join(map(str, conids)),
                'fields': MARKET_DATA_FIELDS
            }
            response = requests.get(url, params=params, verify=False)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching live market data: {str(e)}")
            raise

    @staticmethod
    def calculate_adjusted_price(current_price, side, adjustment_percent=PRICE_ADJUSTMENT_PERCENT):
        """Calculate adjusted price based on order side"""
        if side.upper() == 'BUY':
            # For buy orders, reduce price by adjustment_percent
            return current_price * (1 - adjustment_percent)
        elif side.upper() == 'SELL':
            # For sell orders, increase price by adjustment_percent
            return current_price * (1 + adjustment_percent)
        return current_price

    @staticmethod
    def get_optimal_order_price(conid, side):
        """Get optimal order price based on current market data"""
        try:
            market_data = MarketDataService.get_live_market_data([conid])
            if not market_data:
                return None

            # Extract current price from market data
            current_price = float(market_data[0].get('31', 0))  # Field 31 is last price
            
            # Calculate adjusted price based on order side
            adjusted_price = MarketDataService.calculate_adjusted_price(current_price, side)
            
            return {
                'current_price': current_price,
                'adjusted_price': adjusted_price,
                'adjustment_percent': PRICE_ADJUSTMENT_PERCENT * 100
            }
        except Exception as e:
            logger.error(f"Error calculating optimal order price: {str(e)}")
            return None 