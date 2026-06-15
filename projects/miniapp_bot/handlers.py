"""
MiniAppBot 事件处理器
"""
import logging
import requests
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ParseMode
from telegram.ext import ContextTypes

from config import (
    SHARED_API_URL, API_BOT_TOKEN, MINIAPP_URL, JWT_SECRET,
    TASK_DAILY_CHECKIN_POINTS, TASK_FIRST_MESSAGE_POINTS,
    TASK_INVITE_USER_POINTS, LEADERBOARD_SIZE
)
from utils import generate_access_token

logger = logging.getLogger(__name__)

# API请求头
HEADERS = {
    'X-Bot-Token': API_BOT_TOKEN,
    'Content-Type': 'application/json'
}


# ============ 积分查询 ============
async def cmd_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查询用户积分"""
    try:
        user_id = update.effective_user.id

        # 获取用户积分
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}/points",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取积分失败")
            return

        data = response.json().get('data', {})
        points = data.get('points', 0)
        level = data.get('level', 1)

        # 计算排名
        leaderboard_response = requests.get(
            f"{SHARED_API_URL}/leaderboard?limit=1000",
            headers=HEADERS,
            timeout=5
        )

        rank = 1
        if leaderboard_response.status_code == 200:
            leaderboard = leaderboard_response.json().get('data', {}).get('leaderboard', [])
            for idx, user in enumerate(leaderboard, 1):
                if user.get('user_id') == user_id:
                    rank = idx
                    break

        await update.message.reply_text(
            f"💰 *你的积分信息*\n\n"
            f"总积分: `{points}`\n"
            f"等级: `Lv{level}`\n"
            f"排名: `第{rank}名`",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"查询积分失败: {e}")
        await update.message.reply_text(f"❌ 查询失败: {e}")


# ============ 排行榜 ============
async def cmd_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示排行榜"""
    try:
        response = requests.get(
            f"{SHARED_API_URL}/leaderboard?limit={LEADERBOARD_SIZE}",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取排行榜失败")
            return

        leaderboard = response.json().get('data', {}).get('leaderboard', [])

        message = "🏆 *积分排行榜 (Top 10)*\n\n"
        for idx, user in enumerate(leaderboard, 1):
            username = user.get('username', f"用户{user.get('user_id')}")
            points = user.get('points', 0)
            medal = ['🥇', '🥈', '🥉']
            medal_str = medal[idx - 1] if idx <= 3 else f"{idx}️⃣"
            message += f"{medal_str} {username}: `{points}` 分\n"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取排行榜失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")


# ============ 打开Mini App ============
async def cmd_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """打开Mini App"""
    try:
        user = update.effective_user
        user_id = user.id

        # 生成访问令牌
        token = generate_access_token(user_id)

        # 创建Mini App按钮
        web_app = WebAppInfo(url=f"{MINIAPP_URL}?token={token}&user_id={user_id}")
        buttons = [[InlineKeyboardButton(
            text="🎮 打开小程序",
            web_app=web_app
        )]]

        await update.message.reply_text(
            "🎮 点击下方按钮打开小程序\n\n"
            "在小程序中你可以:\n"
            "✅ 完成任务赚取积分\n"
            "✅ 查看个人成就\n"
            "✅ 参与排行榜\n"
            "✅ 获取奖励",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        logger.info(f"用户{user_id}打开Mini App")

    except Exception as e:
        logger.error(f"打开Mini App失败: {e}")
        await update.message.reply_text(f"❌ 打开失败: {e}")


# ============ 日常签到 ============
async def cmd_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """每日签到"""
    try:
        user_id = update.effective_user.id

        # 检查是否已签到过
        user_response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}",
            headers=HEADERS,
            timeout=5
        )

        if user_response.status_code != 200:
            await update.message.reply_text("❌ 获取用户信息失败")
            return

        user = user_response.json().get('data', {})
        last_checkin = user.get('last_checkin')

        # 检查是否是同一天
        if last_checkin:
            last_checkin_date = datetime.fromisoformat(last_checkin).date()
            today = datetime.now().date()
            if last_checkin_date == today:
                await update.message.reply_text(
                    f"⏰ 你今天已经签到过了！\n"
                    f"明天再来吧 😊"
                )
                return

        # 增加积分
        points_response = requests.post(
            f"{SHARED_API_URL}/users/{user_id}/add-points",
            json={
                'points': TASK_DAILY_CHECKIN_POINTS,
                'reason': 'daily_checkin'
            },
            headers=HEADERS,
            timeout=5
        )

        if points_response.status_code == 200:
            data = points_response.json().get('data', {})
            new_points = data.get('new_points', 0)

            # 更新签到时间
            requests.post(
                f"{SHARED_API_URL}/users",
                json={
                    'user_id': user_id,
                    'last_checkin': datetime.now().isoformat()
                },
                headers=HEADERS,
                timeout=5
            )

            await update.message.reply_text(
                f"✅ *签到成功！*\n\n"
                f"获得积分: `+{TASK_DAILY_CHECKIN_POINTS}`\n"
                f"当前总积分: `{new_points}`",
                parse_mode=ParseMode.MARKDOWN
            )

            logger.info(f"用户{user_id}完成每日签到")
        else:
            await update.message.reply_text("❌ 签到失败，请稍后重试")

    except Exception as e:
        logger.error(f"签到失败: {e}")
        await update.message.reply_text(f"❌ 签到失败: {e}")


# ============ 任务列表 ============
async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示任务列表"""
    try:
        message = (
            "📋 *可用任务*\n\n"
            "⏰ *每日任务*\n"
            f"📅 每日签到 - 奖励 `{TASK_DAILY_CHECKIN_POINTS}` 积分\n"
            f"💬 发送第一条消息 - 奖励 `{TASK_FIRST_MESSAGE_POINTS}` 积分\n\n"
            "👥 *邀请任务*\n"
            f"🔗 邀请新用户 - 奖励 `{TASK_INVITE_USER_POINTS}` 积分\n\n"
            "🎮 点击 `/play` 在小程序中查看更多任务"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")


# ============ 统计信息 ============
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看个人统计"""
    try:
        user_id = update.effective_user.id

        # 获取用户数据
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}/activity-log?limit=100",
            headers=HEADERS,
            timeout=5
        )

        if response.status_code != 200:
            await update.message.reply_text("❌ 获取统计失败")
            return

        logs = response.json().get('data', {}).get('logs', [])

        # 统计各类事件
        completed_tasks = len([l for l in logs if l.get('action') == 'task_completed'])
        points_earned = sum([l.get('points_earned', 0) for l in logs if l.get('action') == 'task_completed'])

        message = (
            f"📊 *个人统计*\n\n"
            f"✅ 完成任务: `{completed_tasks}` 个\n"
            f"💰 获得积分: `{points_earned}` 分\n"
            f"📈 最近活动: `{len(logs)}` 条记录"
        )

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        await update.message.reply_text(f"❌ 获取失败: {e}")
