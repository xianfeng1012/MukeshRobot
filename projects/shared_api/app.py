"""
共享API服务器 - Telegram三Bot数据中心
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import redis
import jwt

from config import (
    MONGO_URI, MONGO_DB, REDIS_URL, API_HOST, API_PORT, API_DEBUG,
    JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS,
    API_BOT_TOKEN,
    MINIAPP_SECRET, LOG_LEVEL, LOG_FILE
)
from models import *

# ============ 日志配置 ============
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ Flask应用初始化 ============
app = Flask(__name__)
CORS(app)

# ============ 数据库连接 ============
try:
    mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo.admin.command('ping')
    db = mongo[MONGO_DB]
    logger.info("MongoDB连接成功")
except ServerSelectionTimeoutError as e:
    logger.error(f"MongoDB连接失败: {e}")
    db = None

try:
    redis_client = redis.from_url(REDIS_URL)
    redis_client.ping()
    logger.info("Redis连接成功")
except Exception as e:
    logger.error(f"Redis连接失败: {e}")
    redis_client = None

# ============ 认证装饰器 ============
def token_required(f):
    """验证API Token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'code': 401, 'message': 'Missing token'}), 401

        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = data.get('user_id')
            request.bot_type = data.get('bot_type')
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated


def bot_token_required(f):
    """验证Bot Token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Bot-Token')

        if token != API_BOT_TOKEN:
            return jsonify({'code': 401, 'message': 'Invalid bot token'}), 401

        return f(*args, **kwargs)
    return decorated


# ============ 工具函数 ============
def generate_token(user_id: int, bot_type: str = 'user'):
    """生成JWT Token"""
    payload = {
        'user_id': user_id,
        'bot_type': bot_type,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ============ 健康检查 ============
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'code': 200,
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    })


# ============ 用户接口 ============
@app.route('/api/users/<int:user_id>', methods=['GET'])
@bot_token_required
def get_user(user_id: int):
    """获取用户信息"""
    try:
        user = db.users.find_one({'user_id': user_id})
        if not user:
            return jsonify({'code': 404, 'message': 'User not found'}), 404

        user.pop('_id', None)
        return jsonify({'code': 200, 'data': user})
    except Exception as e:
        logger.error(f"获取用户失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/users', methods=['POST'])
@bot_token_required
def create_or_update_user():
    """创建或更新用户"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'code': 400, 'message': 'user_id is required'}), 400

        # 如果用户不存在，添加创建时间
        existing = db.users.find_one({'user_id': user_id})
        if not existing:
            data['created_at'] = datetime.now()

        data['last_active'] = datetime.now()

        db.users.update_one(
            {'user_id': user_id},
            {'$set': data},
            upsert=True
        )

        return jsonify({'code': 200, 'message': 'success'})
    except Exception as e:
        logger.error(f"创建/更新用户失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 积分接口 ============
@app.route('/api/users/<int:user_id>/points', methods=['GET'])
@bot_token_required
def get_points(user_id: int):
    """获取用户积分"""
    try:
        user = db.users.find_one({'user_id': user_id})
        points = user.get('points', 0) if user else 0

        return jsonify({
            'code': 200,
            'data': {
                'user_id': user_id,
                'points': points,
                'level': user.get('level', 1) if user else 1
            }
        })
    except Exception as e:
        logger.error(f"获取积分失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/users/<int:user_id>/add-points', methods=['POST'])
@bot_token_required
def add_points(user_id: int):
    """增加积分"""
    try:
        data = request.json
        points = data.get('points', 0)
        reason = data.get('reason', 'unknown')

        # 更新积分
        result = db.users.update_one(
            {'user_id': user_id},
            {'$inc': {'points': points}},
            upsert=True
        )

        # 记录活动日志
        db.activity_logs.insert_one({
            'user_id': user_id,
            'action': 'points_added',
            'amount': points,
            'reason': reason,
            'timestamp': datetime.now()
        })

        # 缓存积分
        if redis_client:
            redis_client.set(f"user:{user_id}:points", points, ex=3600)

        # 获取更新后的积分
        user = db.users.find_one({'user_id': user_id})
        new_points = user.get('points', 0) if user else 0

        logger.info(f"用户{user_id}增加{points}积分，原因: {reason}")

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'user_id': user_id,
                'new_points': new_points
            }
        })
    except Exception as e:
        logger.error(f"增加积分失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 黑名单接口 ============
@app.route('/api/blacklist/check/<int:user_id>', methods=['GET'])
@bot_token_required
def check_blacklist(user_id: int):
    """检查用户是否被屏蔽"""
    try:
        user = db.users.find_one({'user_id': user_id})
        is_blacklisted = user.get('blacklisted', False) if user else False

        return jsonify({
            'code': 200,
            'data': {
                'user_id': user_id,
                'blacklisted': is_blacklisted
            }
        })
    except Exception as e:
        logger.error(f"检查黑名单失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/blacklist/add', methods=['POST'])
@bot_token_required
def add_to_blacklist():
    """添加到黑名单"""
    try:
        data = request.json
        user_id = data.get('user_id')
        reason = data.get('reason', 'unknown')
        added_by = data.get('added_by')

        db.users.update_one(
            {'user_id': user_id},
            {'$set': {'blacklisted': True}},
            upsert=True
        )

        db.blacklist.insert_one({
            'user_id': user_id,
            'reason': reason,
            'added_by': added_by,
            'added_at': datetime.now()
        })

        logger.warning(f"用户{user_id}被添加到黑名单，原因: {reason}")

        return jsonify({'code': 200, 'message': 'success'})
    except Exception as e:
        logger.error(f"添加黑名单失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 群组设置接口 ============
DEFAULT_GROUP_SETTINGS = {
    'welcome_text': None,
    'verify_enabled': True,
    'spam_enabled': True,
}


@app.route('/api/groups/<chat_id>/settings', methods=['GET'])
@bot_token_required
def get_group_settings(chat_id):
    """获取群组设置（不存在则返回默认值）"""
    try:
        cid = int(chat_id)
        data = dict(DEFAULT_GROUP_SETTINGS)
        settings = db.group_settings.find_one({'chat_id': cid})
        if settings:
            settings.pop('_id', None)
            for k in DEFAULT_GROUP_SETTINGS:
                if k in settings:
                    data[k] = settings[k]
        data['chat_id'] = cid
        return jsonify({'code': 200, 'data': data})
    except Exception as e:
        logger.error(f"获取群组设置失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/groups/<chat_id>/settings', methods=['POST'])
@bot_token_required
def update_group_settings(chat_id):
    """更新群组设置（仅接受已知字段）"""
    try:
        cid = int(chat_id)
        data = request.json or {}
        update = {k: data[k] for k in DEFAULT_GROUP_SETTINGS if k in data}
        if not update:
            return jsonify({'code': 400, 'message': 'no valid fields'}), 400

        update['updated_at'] = datetime.now()
        db.group_settings.update_one(
            {'chat_id': cid},
            {'$set': update},
            upsert=True
        )
        logger.info(f"更新群组{cid}设置: {list(update.keys())}")
        return jsonify({'code': 200, 'message': 'success'})
    except Exception as e:
        logger.error(f"更新群组设置失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 群成员（新人观察期）接口 ============
@app.route('/api/group-members', methods=['POST'])
@bot_token_required
def upsert_group_member():
    """记录/更新群成员（首次写入时记录入群时间，默认进入观察期）"""
    try:
        data = request.json or {}
        chat_id = data.get('chat_id')
        user_id = data.get('user_id')
        if chat_id is None or user_id is None:
            return jsonify({'code': 400, 'message': 'chat_id and user_id required'}), 400

        existing = db.group_members.find_one({'chat_id': chat_id, 'user_id': user_id})
        doc = {'chat_id': chat_id, 'user_id': user_id}
        if not existing:
            doc['joined_at'] = datetime.now()
            doc['status'] = data.get('status', 'probation')
        elif 'status' in data:
            doc['status'] = data['status']

        db.group_members.update_one(
            {'chat_id': chat_id, 'user_id': user_id},
            {'$set': doc},
            upsert=True
        )
        return jsonify({'code': 200, 'message': 'success'})
    except Exception as e:
        logger.error(f"记录群成员失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/group-members/<chat_id>/<int:user_id>', methods=['GET'])
@bot_token_required
def get_group_member(chat_id, user_id: int):
    """获取群成员状态"""
    try:
        member = db.group_members.find_one({'chat_id': int(chat_id), 'user_id': user_id})
        if not member:
            return jsonify({'code': 404, 'message': 'not found'}), 404
        member.pop('_id', None)
        if isinstance(member.get('joined_at'), datetime):
            member['joined_at'] = member['joined_at'].isoformat()
        return jsonify({'code': 200, 'data': member})
    except Exception as e:
        logger.error(f"获取群成员失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/group-members/<chat_id>/<int:user_id>', methods=['DELETE'])
@bot_token_required
def delete_group_member(chat_id, user_id: int):
    """删除群成员记录（如验证超时被踢）"""
    try:
        db.group_members.delete_one({'chat_id': int(chat_id), 'user_id': user_id})
        return jsonify({'code': 200, 'message': 'success'})
    except Exception as e:
        logger.error(f"删除群成员失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


@app.route('/api/group-members/expired', methods=['GET'])
@bot_token_required
def get_expired_members():
    """返回所有仍处于观察期、且入群已满 N 天的成员"""
    try:
        days = int(request.args.get('days', 3))
        cutoff = datetime.now() - timedelta(days=days)
        members = db.group_members.find({
            'status': 'probation',
            'joined_at': {'$lte': cutoff}
        })
        result = [{'chat_id': m['chat_id'], 'user_id': m['user_id']} for m in members]
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        logger.error(f"查询观察期到期成员失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 活动日志接口 ============
@app.route('/api/users/<int:user_id>/activity-log', methods=['GET'])
@bot_token_required
def get_activity_log(user_id: int):
    """获取用户活动记录"""
    try:
        limit = request.args.get('limit', 50, type=int)

        logs = list(db.activity_logs.find(
            {'user_id': user_id},
            sort=[('timestamp', -1)],
            limit=limit
        ))

        for log in logs:
            log.pop('_id', None)

        return jsonify({
            'code': 200,
            'data': {
                'user_id': user_id,
                'logs': logs,
                'total': len(logs)
            }
        })
    except Exception as e:
        logger.error(f"获取活动日志失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 排行榜接口 ============
@app.route('/api/leaderboard', methods=['GET'])
@bot_token_required
def get_leaderboard():
    """获取积分排行榜"""
    try:
        limit = request.args.get('limit', 10, type=int)

        leaderboard = list(db.users.find(
            {'blacklisted': False},
            {'user_id': 1, 'username': 1, 'points': 1, 'level': 1},
            sort=[('points', -1)],
            limit=limit
        ))

        for user in leaderboard:
            user.pop('_id', None)

        return jsonify({
            'code': 200,
            'data': {
                'leaderboard': leaderboard,
                'total': len(leaderboard)
            }
        })
    except Exception as e:
        logger.error(f"获取排行榜失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ Mini App Webhook ============
@app.route('/api/webhook/mini-app-event', methods=['POST'])
def handle_mini_app_event():
    """处理Mini App事件"""
    try:
        data = request.json
        event_type = data.get('event_type')
        user_id = data.get('user_id')

        logger.info(f"收到Mini App事件: {event_type}, 用户: {user_id}")

        if event_type == 'task_completed':
            points = data.get('points', 0)
            task_id = data.get('task_id')

            # 更新积分
            db.users.update_one(
                {'user_id': user_id},
                {'$inc': {'points': points}},
                upsert=True
            )

            # 记录日志
            db.activity_logs.insert_one({
                'user_id': user_id,
                'action': 'task_completed',
                'task_id': task_id,
                'points_earned': points,
                'timestamp': datetime.now()
            })

            return jsonify({'code': 200, 'message': 'success'})

        elif event_type == 'daily_checkin':
            db.users.update_one(
                {'user_id': user_id},
                {'$inc': {'points': 50}},
                upsert=True
            )

            return jsonify({'code': 200, 'message': 'success'})

        else:
            return jsonify({'code': 400, 'message': 'Unknown event type'}), 400

    except Exception as e:
        logger.error(f"处理Mini App事件失败: {e}")
        return jsonify({'code': 500, 'message': str(e)}), 500


# ============ 错误处理 ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'code': 404, 'message': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'code': 500, 'message': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info(f"启动API服务器: {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=API_DEBUG)
