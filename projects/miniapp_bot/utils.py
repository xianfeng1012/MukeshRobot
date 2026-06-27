"""
MiniAppBot 工具函数
"""
import jwt
from datetime import datetime, timedelta
from config import JWT_SECRET, JWT_EXPIRATION_HOURS, JWT_ALGORITHM


def generate_access_token(user_id: int, bot_type: str = 'miniapp') -> str:
    """生成Mini App访问令牌"""
    payload = {
        'user_id': user_id,
        'bot_type': bot_type,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """验证令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}
