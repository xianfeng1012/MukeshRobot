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

# 导航(/guide)与底部菜单相关链接
GUIDE_FEATURED_LINK = os.getenv('GUIDE_FEATURED_LINK', 'https://t.me/+WMN56KjIDZUyNWNl')   # 精品榜频道
GUIDE_PARTTIME_LINK = os.getenv('GUIDE_PARTTIME_LINK', 'https://t.me/+383KB9684EUyNGZl')   # 兼职榜频道
GUIDE_NEWBIE_LINK = os.getenv('GUIDE_NEWBIE_LINK', 'https://t.me/+eqndBOD1NdhiZWRl')        # 新生榜频道
GUIDE_MINIAPP_LINK = os.getenv('GUIDE_MINIAPP_LINK', 'https://t.me/llxxsv2bot/app')         # 小程序(看评论)
GUIDE_OWNER_LINK = os.getenv('GUIDE_OWNER_LINK', 'https://t.me/lanlingwangbot')             # 群主(双向机器人私聊)

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = '/tmp/user_bot.log'
