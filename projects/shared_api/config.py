"""
共享API配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = 'telegram_bot_db'

# Redis
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# API配置
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
API_DEBUG = os.getenv('API_DEBUG', 'True') == 'True'

# Bot Tokens（用于验证请求）
GROUP_BOT_TOKEN = os.getenv('GROUP_BOT_TOKEN')
MINIAPP_BOT_TOKEN = os.getenv('MINIAPP_BOT_TOKEN')
USER_BOT_TOKEN = os.getenv('USER_BOT_TOKEN')

# Mini App配置
MINIAPP_SECRET = os.getenv('MINIAPP_SECRET', 'your-secret-key-change-me')
MINIAPP_URL = os.getenv('MINIAPP_URL', 'https://miniapp.example.com')
MINIAPP_WEBHOOK_SECRET = os.getenv('MINIAPP_WEBHOOK_SECRET', 'webhook-secret')

# JWT配置
JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-change-me')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# 日志
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'shared_api.log'

# 数据库池配置
MONGO_POOL_SIZE = 50
MONGO_TIMEOUT = 5000  # ms
