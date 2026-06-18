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

# Mini App配置（/play 打开的小程序直链）
MINIAPP_URL = os.getenv('MINIAPP_URL', 'https://t.me/llxxsv2bot/app')
MINIAPP_SECRET = os.getenv('MINIAPP_SECRET', 'your-secret-key')
MINIAPP_WEBHOOK_URL = os.getenv('MINIAPP_WEBHOOK_URL', 'http://localhost:8000/webhook/mini-app-event')
MINIAPP_WEBHOOK_PORT = int(os.getenv('MINIAPP_WEBHOOK_PORT', 8000))

# JWT配置
JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret-change-me')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# yanyulou 项目 API（积分/签到/排行榜的真实数据源）
YANYULOU_API_BASE = os.getenv('YANYULOU_API_BASE', 'https://api.ooxxooxx.dpdns.org')
YANYULOU_API_KEY = os.getenv('YANYULOU_API_KEY', 'dev-bot-api-key')

# 小程序前端（TMA）地址，用于深链到指定资料页 /girls/<id>
YANYULOU_TMA_BASE = os.getenv('YANYULOU_TMA_BASE', 'https://ooxxooxx.dpdns.org')

# 本机器人用户名（频道按钮深链 t.me/<bot>?start= 用）
BOT_USERNAME = os.getenv('BOT_USERNAME', 'llxxsv2bot')

# 资料发布 Webhook（yanyulou admin → 本机器人）
PUBLISH_SECRET = os.getenv('TG_PUBLISH_SECRET', 'yanyulou-tg-publish-2024')
PUBLISH_WEBHOOK_PORT = int(os.getenv('PUBLISH_WEBHOOK_PORT', 8000))

# 分类 → 频道映射（精品/兼职/新生）
CHANNEL_FEATURED = int(os.getenv('CHANNEL_FEATURED', -1002665963207))
CHANNEL_PART_TIME = int(os.getenv('CHANNEL_PART_TIME', -1004417011478))
CHANNEL_NEWBIE = int(os.getenv('CHANNEL_NEWBIE', -1004298729775))

# 分类 → 频道公开/邀请链接（「今日开课」底部按钮跳转用，数字ID不能做URL按钮）
CHANNEL_LINK_FEATURED = os.getenv('CHANNEL_LINK_FEATURED', 'https://t.me/+WMN56KjIDZUyNWNl')
CHANNEL_LINK_PART_TIME = os.getenv('CHANNEL_LINK_PART_TIME', 'https://t.me/+383KB9684EUyNGZl')
CHANNEL_LINK_NEWBIE = os.getenv('CHANNEL_LINK_NEWBIE', 'https://t.me/+eqndBOD1NdhiZWRl')

# 「今日开课」只回答本群所属城市的资料（成都群只列成都；多城市群后续单独配置）
SCHEDULE_CITY = os.getenv('SCHEDULE_CITY', '成都')

# 每日定时发布「今日开课」的目标频道（公示榜）
SCHEDULE_CHANNEL_ID = int(os.getenv('SCHEDULE_CHANNEL_ID', -1004378375166))

# 排行榜配置
LEADERBOARD_SIZE = 10

# 日志
LOG_LEVEL = 'INFO'
LOG_FILE = '/tmp/miniapp_bot.log'

# 功能开关
POINTS_SYSTEM_ENABLED = True
LEADERBOARD_ENABLED = True
MINIAPP_INTEGRATION_ENABLED = True
