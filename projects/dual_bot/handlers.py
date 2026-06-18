"""
DualBot 事件处理器
- 客户私聊某机器人 → 在客服群发身份头 + copy 客户消息，并记录映射。
- 客服在群里 reply 某条客户消息 → 源机器人查映射，copy 回传给该客户。
- 隐私模式开启时，每个机器人在群里只会收到「对它自己消息的回复」，
  因此多号共群也能天然路由、不串号、不重复。
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import SUPPORT_GROUP_ID
from db import save_relay, find_customer

logger = logging.getLogger(__name__)


async def on_customer_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """客户私聊入站：转发到客服群（身份头 + 原消息），并记录映射。"""
    msg = update.effective_message
    user = update.effective_user
    if msg is None or user is None:
        return

    label = context.bot_data.get('label', 'Bot')
    uname = f"@{user.username}" if user.username else "无用户名"
    header = f"👤 {user.full_name} ({uname} / id:{user.id}) ·〔{label}〕"

    try:
        h = await context.bot.send_message(SUPPORT_GROUP_ID, header)
        c = await context.bot.copy_message(
            chat_id=SUPPORT_GROUP_ID,
            from_chat_id=user.id,
            message_id=msg.message_id,
        )
        # header 和正文都建映射：客服回复哪条都能定位到客户
        save_relay(c.message_id, user.id, context.bot.id)
        save_relay(h.message_id, user.id, context.bot.id)
        logger.info(f"[{label}] 已转发客户 {user.id} 消息到群")
    except Exception as e:
        logger.error(f"[{label}] 转发客户 {user.id} 消息到群失败: {e}")


async def on_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """客服群内 reply：查映射 → 把客服内容 copy 回传给对应客户。"""
    msg = update.effective_message
    if msg is None or msg.reply_to_message is None:
        return

    doc = find_customer(msg.reply_to_message.message_id)
    if not doc:
        return  # 不是回复客户消息（客服内部讨论 / 老消息已无映射）→ 忽略

    # 安全兜底：若关掉隐私模式导致多号都收到，只让源机器人回传
    if doc.get('bot_id') and doc['bot_id'] != context.bot.id:
        return

    customer_id = doc['customer_id']
    try:
        await context.bot.copy_message(
            chat_id=customer_id,
            from_chat_id=SUPPORT_GROUP_ID,
            message_id=msg.message_id,
        )
        logger.info(f"[{context.bot_data.get('label')}] 已回传客户 {customer_id}")
    except Exception as e:
        logger.error(f"回传客户 {customer_id} 失败: {e}")
        try:
            await msg.reply_text(f"⚠️ 回传失败（客户可能已拉黑机器人）：{e}")
        except Exception:
            pass


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/id：返回当前会话 chat id（部署时取客服群 ID 用）。仅主实例响应，避免多号刷屏。"""
    if not context.bot_data.get('primary'):
        return
    chat = update.effective_chat
    if chat is None:
        return
    await update.message.reply_text(f"chat id: `{chat.id}`", parse_mode='Markdown')
