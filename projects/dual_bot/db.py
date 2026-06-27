"""
DualBot 会话映射存储（MongoDB）
dual_relay: 客服群里某条消息ID → 该消息对应的客户。
客服 reply 群里消息时，靠这张表查回是哪个客户、哪个机器人发出去。
"""
import time
import logging
from pymongo import MongoClient

from config import MONGO_URI, MONGO_DB

logger = logging.getLogger(__name__)

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB]
_relay = _db['dual_relay']

# 按群消息ID查；唯一索引避免重复
_relay.create_index('group_msg_id', unique=True)


def save_relay(group_msg_id: int, customer_id: int, bot_id: int):
    """记录：客服群里这条消息 → 客户。header 和正文各存一条，客服回复哪条都能定位。"""
    try:
        _relay.update_one(
            {'group_msg_id': group_msg_id},
            {'$set': {
                'group_msg_id': group_msg_id,
                'customer_id': customer_id,
                'bot_id': bot_id,
                'ts': time.time(),
            }},
            upsert=True,
        )
    except Exception as e:
        logger.error(f"保存映射失败 group_msg_id={group_msg_id}: {e}")


def find_customer(group_msg_id: int):
    """按被回复的群消息ID查客户映射，查不到返回 None。"""
    try:
        return _relay.find_one({'group_msg_id': group_msg_id})
    except Exception as e:
        logger.error(f"查询映射失败 group_msg_id={group_msg_id}: {e}")
        return None
