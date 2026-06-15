"""
UserBot 事件处理器
"""
import logging
import requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import ContextTypes

from config import SHARED_API_URL, API_BOT_TOKEN

logger = logging.getLogger(__name__)

HEADERS = {
    'X-Bot-Token': API_BOT_TOKEN,
    'Content-Type': 'application/json'
}


# ============ 个人档案 ============
async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看个人档案"""
    try:
        user_id = update.effective_user.id
        user = update.effective_user

        # 获取用户数据
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取档案失败")
            return

        user_data = response.json().get('data', {})

        profile_text = (
            f"👤 *个人档案*\n\n"
            f"*基本信息*\n"
            f"用户名: @{user.username or '未设置'}\n"
            f"昵称: {user.first_name} {user.last_name or ''}\n"
            f"ID: `{user_id}`\n\n"
            f"*积分统计*\n"
            f"💰 积分: `{user_data.get('points', 0)}`\n"
            f"📈 等级: `Lv{user_data.get('level', 1)}`\n"
            f"🎖️ 成就: `{len(user_data.get('achievements', []))}` 个\n\n"
            f"*群组信息*\n"
            f"📊 信誉分: `{user_data.get('reputation_score', 100)}/100`\n"
            f"⚠️ 违规次数: `{user_data.get('violations', 0)}`\n"
            f"🚫 黑名单: {'是' if user_data.get('blacklisted') else '否'}\n\n"
            f"*其他*\n"
            f"🏷️ 头衔: {', '.join(user_data.get('titles', [])) or '无'}\n"
            f"📅 加入时间: {user_data.get('created_at', '').split('T')[0]}"
        )

        await update.message.reply_text(profile_text, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取档案失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")


# ============ 活动记录 ============
async def cmd_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看活动记录"""
    try:
        user_id = update.effective_user.id

        # 获取活动日志
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}/activity-log?limit=20",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取记录失败")
            return

        logs = response.json().get('data', {}).get('logs', [])

        if not logs:
            await update.message.reply_text("📭 暂无活动记录")
            return

        message = "📋 *最近活动 (最新20条)*\n\n"
        for log in logs[:20]:
            action = log.get('action', 'unknown')
            timestamp = log.get('timestamp', '')
            if timestamp:
                timestamp = datetime.fromisoformat(timestamp).strftime('%m-%d %H:%M')

            action_text = {
                'points_added': f"💰 获得积分 +{log.get('amount', 0)}",
                'task_completed': f"✅ 完成任务 +{log.get('points_earned', 0)}积分",
                'message_sent': "💬 发送消息",
                'daily_checkin': "📅 每日签到"
            }.get(action, f"📌 {action}")

            message += f"`{timestamp}` {action_text}\n"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取活动记录失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")


# ============ 统计数据 ============
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看统计数据"""
    try:
        user_id = update.effective_user.id

        # 获取活动日志用于统计
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}/activity-log?limit=1000",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取统计失败")
            return

        logs = response.json().get('data', {}).get('logs', [])

        # 统计各类事件
        messages = len([l for l in logs if l.get('action') == 'message_sent'])
        tasks = len([l for l in logs if l.get('action') == 'task_completed'])
        checkins = len([l for l in logs if l.get('action') == 'daily_checkin'])
        total_points = sum([l.get('points_earned', 0) for l in logs if l.get('action') == 'task_completed'])

        message = (
            f"📊 *个人统计数据*\n\n"
            f"💬 发送消息: `{messages}` 条\n"
            f"✅ 完成任务: `{tasks}` 个\n"
            f"📅 签到次数: `{checkins}` 次\n"
            f"💰 获得积分: `{total_points}` 分\n"
            f"📈 总记录数: `{len(logs)}` 条"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")


# ============ 隐私设置 ============
async def cmd_privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """隐私设置"""
    try:
        message = (
            "🔐 *隐私设置*\n\n"
            "目前支持的隐私设置:\n"
            "📊 个人统计 - 是否公开显示\n"
            "👤 个人资料 - 是否对其他用户可见\n"
            "🏆 排行榜 - 是否显示在排行榜中\n\n"
            "💡 提示: 使用 `/privacy set <选项> <开/关>` 来修改\n"
            "例如: `/privacy set stats on` - 公开统计数据"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取隐私设置失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")


# ============ 成就展示 ============
async def cmd_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看成就"""
    try:
        user_id = update.effective_user.id

        # 获取用户数据
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取成就失败")
            return

        user_data = response.json().get('data', {})
        achievements = user_data.get('achievements', [])

        if not achievements:
            message = "🎖️ *我的成就*\n\n暂无成就，继续加油! 💪"
        else:
            message = f"🎖️ *我的成就* ({len(achievements)})\n\n"
            achievement_names = {
                'first_task': "🌟 初心者 - 完成第一个任务",
                'top_scorer': "🏆 高手 - 进入积分排行榜前10",
                'veteran': "👑 老兵 - 连续签到30天",
                'social': "🤝 社交达人 - 邀请5个新用户",
            }
            for ach in achievements:
                ach_text = achievement_names.get(ach, f"🎯 {ach}")
                message += f"✅ {ach_text}\n"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取成就失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")
