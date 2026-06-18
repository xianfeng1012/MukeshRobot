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
VERIFICATION_TIMEOUT = 300  # 秒（新人需在此时间内关注频道并点验证，超时踢出）
VERIFICATION_TEXT = "{user}，欢迎加入！👋"

# 关注频道验证：新人需关注指定频道才能解除禁言。
# group_bot 必须是该频道的管理员，否则无法查询关注状态。
VERIFY_CHANNEL_ID = int(os.getenv('VERIFY_CHANNEL_ID', '0'))          # 频道数字ID（-100...），用于查关注
VERIFY_CHANNEL_LINK = os.getenv('VERIFY_CHANNEL_LINK', '')            # 频道链接，按钮跳转用
VERIFY_CHANNEL_NAME = os.getenv('VERIFY_CHANNEL_NAME', '频道')        # 频道显示名

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
