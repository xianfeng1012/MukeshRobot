"""
MiniAppBot 配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot配置
MINIAPP_BOT_TOKEN = os.getenv('MINIAPP_BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_miniapp_bot_username')

# API配置
SHARED_API_URL = os.getenv('SHARED_API_URL', 'http://localhost:5000/api')
API_BOT_TOKEN = os.getenv('API_BOT_TOKEN')

# Mini App配置
MINIAPP_URL = os.getenv('MINIAPP_URL', 'https://miniapp.example.com')
MINIAPP_SECRET = os.getenv('MINIAPP_SECRET', 'your-secret-key')
MINIAPP_WEBHOOK_URL = os.getenv('MINIAPP_WEBHOOK_URL', 'http://localhost:8000/webhook/mini-app-event')
MINIAPP_WEBHOOK_PORT = int(os.getenv('MINIAPP_WEBHOOK_PORT', 8000))

# JWT配置
JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-change-me')
JWT_EXPIRATION_HOURS = 24

# 任务配置
TASK_DAILY_CHECKIN_POINTS = 50
TASK_FIRST_MESSAGE_POINTS = 10
TASK_INVITE_USER_POINTS = 100

# 排行榜配置
LEADERBOARD_SIZE = 10

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = 'miniapp_bot.log'

# 功能开关
POINTS_SYSTEM_ENABLED = True
LEADERBOARD_ENABLED = True
MINIAPP_INTEGRATION_ENABLED = True
