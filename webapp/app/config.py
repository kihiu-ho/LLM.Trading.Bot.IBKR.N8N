import os

# Base API Configuration
BASE_API_URL = "https://127.0.0.1:5000/v1/api"
ACCOUNT_ID = os.environ.get('IBKR_ACCOUNT_ID')

# Flask Configuration
FLASK_APP_URL = "https://localhost:5056"
FLASK_SECRET_KEY = os.urandom(24)

# MinIO Configuration
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_BUCKET = "n8n"

# NocoDB Configuration
NOCODB_BASE_URL = "http://nocodb:8080"
NOCODB_API_TOKEN = os.environ.get('NOCODB_API_TOKEN')
NOCODB_BASE_ID = os.environ.get('NOCODB_PROJECT_ID')
NOCODB_TABLE_ID = os.environ.get('NOCODB_TABLE_ID')
NOCODB_ORDERS_TABLE_ID = os.environ.get('NOCODB_ORDERS_TABLE_ID')
NOCODB_TRADES_TABLE_ID = os.environ.get('NOCODB_TRADES_TABLE_ID')

# N8N Configuration
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', 'http://n8n:5678/webhook/order-filled')

# Market Data Configuration
MARKET_DATA_FIELDS = "31,7059,84,88,86,85"  # Fields for market data snapshot
PRICE_ADJUSTMENT_PERCENT = 0.02  # 2% price adjustment for buy/sell orders

# Order Configuration
DEFAULT_TIF = "DAY"  # Default Time in Force
ORDER_CHECK_INTERVAL = 20  # Seconds between order status checks 