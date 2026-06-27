"""
UserBot 事件处理器
"""
import logging
import time
import requests
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import (
    SHARED_API_URL, API_BOT_TOKEN,
    GUIDE_FEATURED_LINK, GUIDE_PARTTIME_LINK, GUIDE_NEWBIE_LINK,
    GUIDE_MINIAPP_LINK, GUIDE_OWNER_LINK,
)

logger = logging.getLogger(__name__)

HEADERS = {
    'X-Bot-Token': API_BOT_TOKEN,
    'Content-Type': 'application/json'
}


async def _is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in ('administrator', 'creator')
    except Exception as e:
        logger.warning(f"检查管理员失败: {e}")
        return False


def admin_only(handler):
    """包装斜杠命令：群聊中仅管理员有效，非管理员静默忽略；私聊不限制。"""
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        if chat is not None and chat.type != 'private':
            if not await _is_group_admin(update, context):
                return
        await handler(update, context)
    return wrapped


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


# ============ 积分规则 ============
POINTS_RULES_TEXT = (
    "📊 积分规则\n\n"
    "📅 签到规则：\n"
    "• 发送“签到”，每日签到获得 10 积分\n\n"
    "💬 发言规则：\n"
    "• 发言 1 次，获得 1 积分\n"
    "• 每日获取上限：50 积分\n"
    "• 最小字数长度限制：5\n\n"
    "👥 邀请规则：\n"
    "• 邀请 1 人，获得 20 积分\n"
    "• 每日获取上限：无限制\n\n"
    "🔍 查询积分：\n"
    "• 群组中发送“积分”查询自己的积分值\n\n"
    "🏆 查询排行：\n"
    "• 群组中发送“排行榜”查询积分排名"
)


async def cmd_pointsrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/pointsrules 或 汉字「积分规则」：回复积分规则"""
    await update.message.reply_text(POINTS_RULES_TEXT)


# ============ 导航 ============
def _guide_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("精品榜", url=GUIDE_FEATURED_LINK),
            InlineKeyboardButton("兼职榜", url=GUIDE_PARTTIME_LINK),
            InlineKeyboardButton("新生榜", url=GUIDE_NEWBIE_LINK),
        ],
        [InlineKeyboardButton("积分规则", callback_data="show_points_rules")],
    ])


async def cmd_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/guide 或 汉字「导航」：回复导航信息（锚文本 + 跳转按钮）"""
    text = (
        f'开课老师：<a href="{GUIDE_FEATURED_LINK}">精品榜</a>\n'
        f'看评论：<a href="{GUIDE_MINIAPP_LINK}">OOXX</a>\n'
        f'找群主：<a href="{GUIDE_OWNER_LINK}">兰陵王</a>'
    )
    # disable_web_page_preview=False：尝试展示精品榜频道预览框（私有频道邀请链接可能不渲染）
    await update.message.reply_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=_guide_keyboard(), disable_web_page_preview=False
    )


async def handle_guide_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """导航里「积分规则」按钮：弹出积分规则"""
    query = update.callback_query
    try:
        await query.answer()
        await query.message.reply_text(POINTS_RULES_TEXT)
    except Exception as e:
        logger.error(f"积分规则按钮处理失败: {e}")


# ============ 进群底部菜单（签到/导航/今日开课） ============
# 去重：new_chat_members 与 chat_member 两种进群事件对同一人只弹一次菜单
_menu_recent = {}
_MENU_TTL = 60


def _menu_already(chat_id: int, user_id: int) -> bool:
    now = time.time()
    for k, ts in list(_menu_recent.items()):
        if now - ts > _MENU_TTL:
            _menu_recent.pop(k, None)
    key = (chat_id, user_id)
    if key in _menu_recent:
        return True
    _menu_recent[key] = now
    return False


def _menu_keyboard() -> ReplyKeyboardMarkup:
    """底部快捷菜单：签到/导航/今日开课。selective 仅对目标用户显示。"""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("签到"), KeyboardButton("导航"), KeyboardButton("今日开课")]],
        resize_keyboard=True, is_persistent=True, selective=True,
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/menu 或 汉字「菜单」：任何成员可主动召唤底部快捷菜单（老成员也能用）。"""
    await update.message.reply_text("下方菜单可一键操作 👇", reply_markup=_menu_keyboard())


async def _send_join_menu(context: ContextTypes.DEFAULT_TYPE, chat, member):
    """给新成员弹出底部快捷菜单（仅对该成员可见）。点按钮即以其身份发出对应文字。"""
    if member.is_bot or _menu_already(chat.id, member.id):
        return
    kb = _menu_keyboard()
    try:
        await context.bot.send_message(
            chat.id,
            f"{member.mention_html()} 👋 下方菜单可一键操作 👇",
            parse_mode=ParseMode.HTML, reply_markup=kb,
        )
    except Exception as e:
        logger.error(f"发送进群菜单失败: {e}")


async def handle_join_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """new_chat_members（被他人拉入）"""
    try:
        chat = update.effective_chat
        for member in update.message.new_chat_members:
            await _send_join_menu(context, chat, member)
    except Exception as e:
        logger.error(f"处理进群菜单失败: {e}")


async def handle_join_menu_cm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """chat_member（自己通过邀请链接/搜索进群）"""
    try:
        cmu = update.chat_member
        if cmu is None:
            return
        old_status = cmu.old_chat_member.status
        new_member = cmu.new_chat_member
        new_status = new_member.status
        was_in = old_status in ('member', 'administrator', 'creator', 'restricted')
        now_in = new_status == 'member' or (
            new_status == 'restricted' and getattr(new_member, 'is_member', False)
        )
        if was_in or not now_in:
            return
        await _send_join_menu(context, update.effective_chat, new_member.user)
    except Exception as e:
        logger.error(f"处理chat_member进群菜单失败: {e}")
