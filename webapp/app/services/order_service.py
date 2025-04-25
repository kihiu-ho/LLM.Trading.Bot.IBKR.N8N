import requests
import logging
from datetime import datetime
import json
from ..config import (
    BASE_API_URL, ACCOUNT_ID, NOCODB_BASE_URL, NOCODB_API_TOKEN,
    NOCODB_ORDERS_TABLE_ID, DEFAULT_TIF
)
from .market_data_service import MarketDataService

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def place_order(conid, order_type, price, quantity, side, tif=DEFAULT_TIF):
        """Place an order with price management"""
        try:
            # Get optimal price based on market data
            price_data = MarketDataService.get_optimal_order_price(conid, side)
            if price_data:
                # Use the adjusted price if available
                price = price_data['adjusted_price']
                logger.info(f"Using adjusted price: {price} (original: {price_data['current_price']})")

            data = {
                "orders": [{
                    "conid": conid,
                    "orderType": order_type,
                    "price": price,
                    "quantity": quantity,
                    "side": side,
                    "tif": tif
                }]
            }

            logger.info(f"Placing order: {data}")
            response = requests.post(
                f"{BASE_API_URL}/iserver/account/{ACCOUNT_ID}/orders",
                json=data,
                verify=False
            )

            if response.status_code != 200:
                logger.error(f"Failed to place order: {response.text}")
                return {"error": response.text}, response.status_code

            result = response.json()
            
            # Save order to NocoDB if response contains order details
            if len(result) > 0:
                order_response = result[0]
                OrderService.save_order_to_nocodb(
                    order_data=order_response,
                    conid=conid,
                    order_type=order_type,
                    price=price,
                    quantity=quantity,
                    side=side,
                    tif=tif
                )

            return result

        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {"error": str(e)}, 500

    @staticmethod
    def save_order_to_nocodb(order_data, conid, order_type, price, quantity, side, tif):
        """Save order details to NocoDB"""
        if not all([NOCODB_BASE_URL, NOCODB_API_TOKEN, NOCODB_ORDERS_TABLE_ID]):
            logger.error("NocoDB orders table configuration is incomplete.")
            raise ValueError("NocoDB orders table configuration is incomplete")

        url = f"{NOCODB_BASE_URL}/api/v2/tables/{NOCODB_ORDERS_TABLE_ID}/records"
        headers = {
            "xc-token": NOCODB_API_TOKEN,
            "Content-Type": "application/json"
        }

        payload = {
            "order_id": str(order_data["order_id"]),
            "conid": str(conid),
            "status": order_data["order_status"],
            "order_type": order_type,
            "price": float(price),
            "quantity": int(quantity),
            "side": side,
            "tif": tif,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "order_details": json.dumps(order_data)
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"Saved order {order_data.get('orderId')} to NocoDB")
        except requests.RequestException as e:
            error_msg = f"Error saving order to NocoDB: {str(e)}"
            if e.response:
                error_msg += f" - Response: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) 