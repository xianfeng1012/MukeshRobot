"""
数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ 用户相关模型 ============
class UserCreate(BaseModel):
    """创建用户"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_bot: bool = False


class UserUpdate(BaseModel):
    """更新用户信息"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    points: Optional[int] = None
    level: Optional[int] = None
    reputation_score: Optional[int] = None
    violations: Optional[int] = None
    blacklisted: Optional[bool] = None
    titles: Optional[List[str]] = None
    achievements: Optional[List[str]] = None


class UserResponse(BaseModel):
    """用户响应"""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    points: int = 0
    level: int = 1
    reputation_score: int = 100
    violations: int = 0
    blacklisted: bool = False
    titles: List[str] = []
    achievements: List[str] = []
    created_at: datetime
    last_active: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============ 群组相关模型 ============
class GroupCreate(BaseModel):
    """创建群组"""
    chat_id: int
    chat_title: str


class GroupUpdate(BaseModel):
    """更新群组配置"""
    welcome_enabled: Optional[bool] = None
    verification_enabled: Optional[bool] = None
    spam_filter_level: Optional[str] = None  # low, medium, high
    ad_keywords: Optional[List[str]] = None
    rules: Optional[str] = None


class GroupResponse(BaseModel):
    """群组响应"""
    chat_id: int
    chat_title: str
    welcome_enabled: bool = True
    verification_enabled: bool = True
    spam_filter_level: str = "medium"
    ad_keywords: List[str] = []
    rules: Optional[str] = None
    member_count: int = 0
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============ 任务相关模型 ============
class TaskCreate(BaseModel):
    """创建任务"""
    task_id: str
    user_id: int
    task_type: str  # message_count, daily_checkin, etc
    target: int
    reward_points: int


class TaskUpdate(BaseModel):
    """更新任务"""
    progress: Optional[int] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    user_id: int
    task_type: str
    progress: int
    target: int
    reward_points: int
    completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============ 活动日志模型 ============
class ActivityLogCreate(BaseModel):
    """创建活动日志"""
    user_id: int
    action: str  # message_sent, points_added, etc
    group_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class ActivityLogResponse(BaseModel):
    """活动日志响应"""
    user_id: int
    action: str
    group_id: Optional[int]
    details: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============ 黑名单模型 ============
class BlacklistEntry(BaseModel):
    """黑名单条目"""
    user_id: int
    reason: str
    added_by: int
    added_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============ 响应模型 ============
class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    code: int = 200
    message: str = "success"
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
