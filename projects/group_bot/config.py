"""
GroupBot 配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot配置
GROUP_BOT_TOKEN = os.getenv('GROUP_BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_group_bot_username')

# API配置
SHARED_API_URL = os.getenv('SHARED_API_URL', 'http://localhost:5000/api')
API_BOT_TOKEN = os.getenv('API_BOT_TOKEN')  # 用于验证API请求的Token

# 数据库
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = 'telegram_bot_db'

# 验证配置
VERIFICATION_TIMEOUT = 300  # 秒（需私聊机器人完成数学验证，留足跳转时间）
VERIFICATION_TEXT = "{user}，欢迎加入！👋"

# 新人观察期配置
PROBATION_DAYS = 3  # 新成员入群满 N 天后自动解锁媒体权限

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = '/tmp/group_bot.log'

# 功能开关
WELCOME_ENABLED = True
VERIFICATION_ENABLED = True
SPAM_FILTER_ENABLED = True
AD_FILTER_ENABLED = True
