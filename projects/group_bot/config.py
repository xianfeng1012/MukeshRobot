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
VERIFICATION_TIMEOUT = 120  # 秒
VERIFICATION_TEXT = "{user}，欢迎加入！👋\n请点击下方按钮验证你是真人\n⏱️ 你有 120 秒时间"

# 违规配置
MAX_VIOLATIONS = 3  # 最大违规次数
VIOLATION_TIMEOUT = 86400  # 禁言时长（秒）

# 垃圾过滤配置
SPAM_FILTER_ENABLED = True
AD_KEYWORDS = [
    'viagra', 'casino', 'lottery', '彩票', '赌博',
    'crypto', 'bitcoin', '比特币', '以太坊'
]

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = 'group_bot.log'

# 功能开关
WELCOME_ENABLED = True
VERIFICATION_ENABLED = True
SPAM_FILTER_ENABLED = True
AD_FILTER_ENABLED = True
