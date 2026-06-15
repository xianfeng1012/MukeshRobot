"""
UserBot 配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot配置
USER_BOT_TOKEN = os.getenv('USER_BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_user_bot_username')

# API配置
SHARED_API_URL = os.getenv('SHARED_API_URL', 'http://localhost:5000/api')
API_BOT_TOKEN = os.getenv('API_BOT_TOKEN')

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = 'user_bot.log'
