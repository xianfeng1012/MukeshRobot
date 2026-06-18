"""
DualBot 配置
多个对外机器人共用一个客服群，做客户↔客服双向中转。
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 对外机器人 token 列表（逗号分隔）。加号只需往这里追加 token + 把新号拉进客服群 + 重启。
DUAL_BOT_TOKENS = [t.strip() for t in os.getenv('DUAL_BOT_TOKENS', '').split(',') if t.strip()]

# 客服群 ID（所有机器人都要拉进这个群）
SUPPORT_GROUP_ID = int(os.getenv('SUPPORT_GROUP_ID', '0'))

# MongoDB（复用现有实例，存会话映射）
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongodb:27017')
MONGO_DB = os.getenv('MONGO_DB', 'telegram_bot_db')

# 日志
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
