"""
GroupBot 事件处理器
"""
import logging
import time
import random
import asyncio
import requests
from datetime import datetime
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import (
    SHARED_API_URL, API_BOT_TOKEN, VERIFICATION_TIMEOUT, VERIFICATION_TEXT,
    PROBATION_DAYS
)

logger = logging.getLogger(__name__)

# API请求头
HEADERS = {
    'X-Bot-Token': API_BOT_TOKEN,
    'Content-Type': 'application/json'
}

# 完全禁言：验证期间任何消息都发不出
MUTED_PERMISSIONS = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)

# 观察期权限：仅可发文字，禁所有媒体/贴纸/投票/网页预览
PROBATION_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)

# 普通成员权限：文字 + 媒体均可（链接/转发仍由消息级过滤删除）
NORMAL_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
)

# 群管理员ID短期缓存: chat_id -> (set_of_ids, expire_ts)
_admin_cache = {}
_ADMIN_TTL = 60  # 秒


async def get_admin_ids(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> set:
    """获取群管理员ID集合（带短期缓存）"""
    cached = _admin_cache.get(chat_id)
    if cached and cached[1] > time.time():
        return cached[0]
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        ids = {a.user.id for a in admins}
    except Exception as e:
        logger.error(f"获取管理员列表失败: {e}")
        ids = set()
    _admin_cache[chat_id] = (ids, time.time() + _ADMIN_TTL)
    return ids


# ============ 群成员（观察期）API ============
async def record_member(chat_id: int, user_id: int, status: str = 'probation') -> bool:
    """记录群成员（首次写入会记录入群时间）"""
    try:
        response = requests.post(
            f"{SHARED_API_URL}/group-members",
            json={'chat_id': chat_id, 'user_id': user_id, 'status': status},
            headers=HEADERS,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"记录群成员失败: {e}")
        return False


async def remove_member(chat_id: int, user_id: int) -> bool:
    """删除群成员记录"""
    try:
        response = requests.delete(
            f"{SHARED_API_URL}/group-members/{chat_id}/{user_id}",
            headers=HEADERS,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"删除群成员失败: {e}")
        return False


async def get_expired_members(days: int):
    """获取所有观察期已满的成员"""
    try:
        response = requests.get(
            f"{SHARED_API_URL}/group-members/expired",
            params={'days': days},
            headers=HEADERS,
            timeout=8
        )
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except Exception as e:
        logger.error(f"查询观察期到期成员失败: {e}")
        return []

# 群组设置默认值
DEFAULT_GROUP_SETTINGS = {
    'welcome_text': None,
    'verify_enabled': True,
    'spam_enabled': True,
}

# 群组设置短期缓存（减少高频消息路径上的API调用）: chat_id -> (settings, expire_ts)
_settings_cache = {}
_SETTINGS_TTL = 30  # 秒

# 待验证状态: user_id -> {'chat_id': int, 'group_msg_id': int, 'answer': int}
_pending_verifications = {}

# 机器人用户名缓存（用于生成私聊验证深链接）
_bot_username = None


async def _get_bot_username(context: ContextTypes.DEFAULT_TYPE) -> str:
    """获取并缓存机器人用户名"""
    global _bot_username
    if _bot_username is None:
        me = await context.bot.get_me()
        _bot_username = me.username
    return _bot_username


def generate_math_question():
    """生成一道简单数学题，返回 (题面, 正确答案, 4个选项列表)"""
    op = random.choice(['+', '-', '*'])
    if op == '+':
        a, b = random.randint(1, 20), random.randint(1, 20)
        answer = a + b
    elif op == '-':
        a, b = random.randint(1, 20), random.randint(1, 20)
        if b > a:
            a, b = b, a
        answer = a - b
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
        answer = a * b

    question = f"{a} {op} {b} = ?"

    # 生成3个不重复的干扰项
    options = {answer}
    while len(options) < 4:
        cand = answer + random.randint(-5, 5)
        if cand != answer and cand >= 0:
            options.add(cand)
    options = list(options)
    random.shuffle(options)
    return question, answer, options


def _build_math_keyboard(options):
    """把4个选项排成2x2按钮"""
    btns = [InlineKeyboardButton(str(o), callback_data=f"mv_{o}") for o in options]
    return InlineKeyboardMarkup([btns[:2], btns[2:]])


# ============ 群组设置 ============
async def get_group_settings(chat_id: int) -> dict:
    """获取群组设置（带短期缓存）"""
    cached = _settings_cache.get(chat_id)
    if cached and cached[1] > time.time():
        return cached[0]

    settings = dict(DEFAULT_GROUP_SETTINGS)
    try:
        response = requests.get(
            f"{SHARED_API_URL}/groups/{chat_id}/settings",
            headers=HEADERS,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json().get('data', {})
            for k in DEFAULT_GROUP_SETTINGS:
                if k in data:
                    settings[k] = data[k]
    except Exception as e:
        logger.error(f"获取群组设置失败: {e}")

    _settings_cache[chat_id] = (settings, time.time() + _SETTINGS_TTL)
    return settings


async def update_group_settings(chat_id: int, data: dict) -> bool:
    """更新群组设置并使缓存失效"""
    try:
        response = requests.post(
            f"{SHARED_API_URL}/groups/{chat_id}/settings",
            json=data,
            headers=HEADERS,
            timeout=5
        )
        if response.status_code == 200:
            _settings_cache.pop(chat_id, None)
            return True
        return False
    except Exception as e:
        logger.error(f"更新群组设置失败: {e}")
        return False


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """检查命令发送者是否为群管理员"""
    chat = update.effective_chat
    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        return member.status in ('administrator', 'creator')
    except Exception as e:
        logger.error(f"检查管理员权限失败: {e}")
        return False


# ============ 管理命令 ============
async def cmd_setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """设置欢迎消息：/setwelcome <文本>，可用 {user} 代表新成员名字"""
    chat = update.effective_chat
    if chat.type == 'private':
        await update.message.reply_text("⚠️ 该命令只能在群组中使用")
        return
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ 只有群管理员才能使用此命令")
        return

    text = update.message.text.partition(' ')[2].strip()
    if not text:
        await update.message.reply_text(
            "用法：/setwelcome <欢迎语>\n"
            "可用 {user} 代表新成员名字。\n"
            "示例：/setwelcome 欢迎 {user} 加入本群！"
        )
        return

    if await update_group_settings(chat.id, {'welcome_text': text}):
        await update.message.reply_text("✅ 欢迎消息已设置")
    else:
        await update.message.reply_text("❌ 设置失败，请稍后重试")


async def cmd_toggleverify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """切换进群验证功能"""
    chat = update.effective_chat
    if chat.type == 'private':
        await update.message.reply_text("⚠️ 该命令只能在群组中使用")
        return
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ 只有群管理员才能使用此命令")
        return

    settings = await get_group_settings(chat.id)
    new_val = not settings.get('verify_enabled', True)
    if await update_group_settings(chat.id, {'verify_enabled': new_val}):
        await update.message.reply_text(f"{'✅ 已开启' if new_val else '❌ 已关闭'}进群验证功能")
    else:
        await update.message.reply_text("❌ 操作失败，请稍后重试")


async def cmd_togglespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """切换垃圾消息过滤功能"""
    chat = update.effective_chat
    if chat.type == 'private':
        await update.message.reply_text("⚠️ 该命令只能在群组中使用")
        return
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ 只有群管理员才能使用此命令")
        return

    settings = await get_group_settings(chat.id)
    new_val = not settings.get('spam_enabled', True)
    if await update_group_settings(chat.id, {'spam_enabled': new_val}):
        await update.message.reply_text(f"{'✅ 已开启' if new_val else '❌ 已关闭'}垃圾消息过滤")
    else:
        await update.message.reply_text("❌ 操作失败，请稍后重试")


# ============ 新成员加入处理 ============
async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理新成员加入"""
    try:
        new_members = update.message.new_chat_members
        chat = update.effective_chat

        settings = await get_group_settings(chat.id)
        verify_enabled = settings.get('verify_enabled', True)
        spam_enabled = settings.get('spam_enabled', True)
        welcome_text = settings.get('welcome_text')

        for member in new_members:
            # 跳过机器人
            if member.is_bot:
                continue

            user_id = member.id

            # 1. 检查黑名单
            is_blacklisted = await check_blacklist(user_id)
            if is_blacklisted:
                await context.bot.ban_chat_member(chat.id, user_id)
                logger.warning(f"用户{user_id}被禁止进入（黑名单）")
                continue

            # 2. 创建用户档案
            await create_user(user_id, member)

            # 3. 开启观察期时，记录入群时间（作为3天解锁的起点）
            if spam_enabled:
                await record_member(chat.id, user_id, 'probation')

            # 4. 发送欢迎消息（优先使用自定义欢迎语）
            if welcome_text:
                first_msg = welcome_text.replace('{user}', member.first_name)
            elif verify_enabled:
                first_msg = VERIFICATION_TEXT.format(user=member.first_name)
            else:
                first_msg = f"{member.first_name}，欢迎加入！👋"
            await context.bot.send_message(chat.id, first_msg)

            # 验证功能关闭时，不做数学验证
            if not verify_enabled:
                if spam_enabled:
                    # 直接进入观察期：仅可发文字
                    await context.bot.restrict_chat_member(
                        chat.id, user_id, permissions=PROBATION_PERMISSIONS
                    )
                    await context.bot.send_message(
                        chat.id,
                        f"🛡️ 新成员观察期：{PROBATION_DAYS} 天内仅可发送文字，"
                        f"满 {PROBATION_DAYS} 天后自动解锁图片/视频等。"
                    )
                    logger.info(f"新成员加入(免验证·观察期): {member.first_name}({user_id})")
                else:
                    logger.info(f"新成员加入(免验证·无限制): {member.first_name}({user_id})")
                continue

            # 4. 限制用户权限（先完全禁言）
            await context.bot.restrict_chat_member(
                chat.id,
                user_id,
                permissions=MUTED_PERMISSIONS
            )

            # 5. 发送跳转私聊验证的深链接按钮
            bot_username = await _get_bot_username(context)
            verify_url = f"https://t.me/{bot_username}?start=verify_{chat.id}_{user_id}"
            buttons = [[InlineKeyboardButton(
                text="✅ 点我私聊机器人完成验证",
                url=verify_url
            )]]

            verify_msg = await context.bot.send_message(
                chat.id,
                f"{member.mention_html()}，你已被临时禁言。\n"
                f"请点击下方按钮，私聊机器人答对一道数学题即可解除禁言。\n"
                f"⏱️ 请在 {VERIFICATION_TIMEOUT // 60} 分钟内完成。",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

            # 6. 记录待验证状态 + 设置超时
            _pending_verifications[user_id] = {
                'chat_id': chat.id,
                'group_msg_id': verify_msg.message_id,
            }
            context.job_queue.run_once(
                verify_timeout,
                VERIFICATION_TIMEOUT,
                data={
                    'chat_id': chat.id,
                    'user_id': user_id,
                    'message_id': verify_msg.message_id
                },
                name=f'verify_timeout_{user_id}'
            )

            logger.info(f"新成员加入: {member.first_name}({user_id})")

    except Exception as e:
        logger.error(f"处理新成员加入失败: {e}")


async def verify_timeout(context: ContextTypes.DEFAULT_TYPE):
    """验证超时处理"""
    try:
        job = context.job
        data = job.data

        chat_id = data['chat_id']
        user_id = data['user_id']
        message_id = data['message_id']

        # 检查用户是否已验证
        user = await get_user(user_id)
        if user and user.get('verified'):
            return

        # 未验证，踢出用户
        await context.bot.ban_chat_member(chat_id, user_id)
        try:
            await context.bot.delete_message(chat_id, message_id)
        except Exception:
            pass

        _pending_verifications.pop(user_id, None)
        await remove_member(chat_id, user_id)
        logger.warning(f"用户{user_id}验证超时，已踢出")

    except Exception as e:
        logger.error(f"验证超时处理失败: {e}")


# ============ 私聊数学验证 ============
async def handle_verify_start(update: Update, context: ContextTypes.DEFAULT_TYPE, payload: str):
    """处理 /start verify_<chat_id>_<user_id> 深链接，在私聊中出题"""
    try:
        parts = payload.split('_')
        chat_id = int(parts[1])
        target_user_id = int(parts[2])
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ 验证链接无效。")
        return

    user_id = update.effective_user.id
    if user_id != target_user_id:
        await update.message.reply_text("⚠️ 这条验证链接不是发给你的。")
        return

    question, answer, options = generate_math_question()

    # 保留新成员流程里记录的群消息ID（若存在）
    pending = _pending_verifications.get(user_id, {})
    pending['chat_id'] = chat_id
    pending['answer'] = answer
    _pending_verifications[user_id] = pending

    await update.message.reply_text(
        "👋 欢迎！请完成人机验证后即可在群内发言。\n\n"
        f"🧮 请计算： {question}\n\n"
        "请点击下方正确答案：",
        reply_markup=_build_math_keyboard(options)
    )
    logger.info(f"用户{user_id}开始私聊数学验证（群{chat_id}）")


async def handle_math_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理私聊中数学题答案点击"""
    try:
        query = update.callback_query
        user_id = query.from_user.id

        pending = _pending_verifications.get(user_id)
        if not pending or 'answer' not in pending:
            await query.answer("验证已过期，请重新点击群里的验证链接", show_alert=True)
            return

        chosen = int(query.data.split('_')[1])

        # 答错 -> 换一道新题，直到答对
        if chosen != pending['answer']:
            question, answer, options = generate_math_question()
            pending['answer'] = answer
            await query.answer("❌ 答错了，再来一题")
            await query.edit_message_text(
                f"❌ 答错了，再试一题：\n\n🧮 请计算： {question}\n\n请点击下方正确答案：",
                reply_markup=_build_math_keyboard(options)
            )
            return

        # 答对 -> 解除禁言（开启观察期时只解锁文字，满3天再解锁媒体）
        chat_id = pending['chat_id']
        await update_user(user_id, {'verified': True})

        settings = await get_group_settings(chat_id)
        if settings.get('spam_enabled', True):
            perms = PROBATION_PERMISSIONS
            note = f"\n\n🛡️ 新成员观察期：{PROBATION_DAYS} 天内仅可发文字，之后自动解锁图片/视频。"
        else:
            perms = NORMAL_PERMISSIONS
            note = ""
        await context.bot.restrict_chat_member(chat_id, user_id, permissions=perms)

        # 删除群里的验证提示消息
        group_msg_id = pending.get('group_msg_id')
        if group_msg_id:
            try:
                await context.bot.delete_message(chat_id, group_msg_id)
            except Exception:
                pass

        # 取消超时任务
        try:
            for job in context.job_queue.get_jobs_by_name(f'verify_timeout_{user_id}'):
                job.schedule_removal()
        except Exception:
            pass

        _pending_verifications.pop(user_id, None)

        await query.answer("✅ 验证成功！")
        await query.edit_message_text(f"✅ 验证成功！已为你解除禁言，欢迎回到群组发言！{note}")
        logger.info(f"用户{user_id}通过数学验证")

    except Exception as e:
        logger.error(f"处理数学验证答案失败: {e}")


# ============ 消息审查（删除链接/转发） ============
async def moderate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """删除非管理员发送的链接、转发消息"""
    try:
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user

        if message is None or user is None:
            return

        # 按群设置判断是否开启
        settings = await get_group_settings(chat.id)
        if not settings.get('spam_enabled', True):
            return

        # 管理员不受限制
        if user.id in await get_admin_ids(context, chat.id):
            return

        # 转发消息
        is_forward = message.forward_date is not None

        # 链接（正文或图片说明中的 url / text_link 实体）
        entities = list(message.entities or []) + list(message.caption_entities or [])
        has_link = any(e.type in ('url', 'text_link') for e in entities)

        if is_forward or has_link:
            try:
                await message.delete()
            except Exception:
                pass
            reason = '转发' if is_forward else '链接'
            logger.info(f"删除{reason}消息: 用户{user.id} 群{chat.id}")

    except Exception as e:
        logger.error(f"消息审查失败: {e}")


# ============ 群内斜杠命令自动删除（防刷屏） ============
COMMAND_AUTO_DELETE_SECONDS = 120


async def _delete_message_later(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
    """延时后删除单条消息"""
    await asyncio.sleep(COMMAND_AUTO_DELETE_SECONDS)
    try:
        await context.bot.delete_message(chat_id, message_id)
    except Exception:
        pass


async def cleanup_group_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """群内用户发出的斜杠命令，2分钟后自动删除（私聊不处理）"""
    try:
        message = update.effective_message
        chat = update.effective_chat
        if message is None or chat is None or chat.type == 'private':
            return
        context.application.create_task(
            _delete_message_later(context, chat.id, message.message_id)
        )
    except Exception as e:
        logger.error(f"安排删除群命令失败: {e}")


# ============ 观察期到期自动解锁 ============
async def graduate_probation_users(context: ContextTypes.DEFAULT_TYPE):
    """定时任务：把入群满 PROBATION_DAYS 天的成员解锁为普通权限"""
    try:
        expired = await get_expired_members(PROBATION_DAYS)
        for m in expired:
            chat_id = int(m['chat_id'])
            user_id = int(m['user_id'])
            try:
                await context.bot.restrict_chat_member(
                    chat_id, user_id, permissions=NORMAL_PERMISSIONS
                )
                await record_member(chat_id, user_id, 'normal')
                logger.info(f"用户{user_id}观察期满，已解锁完整权限（群{chat_id}）")
            except Exception as e:
                # 用户可能已退群，删除记录避免重复尝试
                logger.error(f"解锁观察期成员失败 user={user_id} chat={chat_id}: {e}")
                await remove_member(chat_id, user_id)
    except Exception as e:
        logger.error(f"观察期解锁任务失败: {e}")


# ============ 成员离开处理 ============
async def handle_member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理成员离开"""
    try:
        left_member = update.message.left_chat_member
        chat = update.effective_chat

        logger.info(f"成员离开: {left_member.first_name}({left_member.id}), 群组: {chat.title}")

    except Exception as e:
        logger.error(f"处理成员离开失败: {e}")


# ============ API调用函数 ============
async def check_blacklist(user_id: int) -> bool:
    """检查用户是否在黑名单"""
    try:
        response = requests.get(
            f"{SHARED_API_URL}/blacklist/check/{user_id}",
            headers=HEADERS,
            timeout=5
        )
        data = response.json()
        return data.get('data', {}).get('blacklisted', False)
    except Exception as e:
        logger.error(f"检查黑名单失败: {e}")
        return False


async def get_user(user_id: int):
    """获取用户信息"""
    try:
        response = requests.get(
            f"{SHARED_API_URL}/users/{user_id}",
            headers=HEADERS,
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get('data')
        return None
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return None


async def create_user(user_id: int, member):
    """创建用户档案"""
    try:
        data = {
            'user_id': user_id,
            'username': member.username,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'is_bot': member.is_bot,
            'verified': False,
            'violations': 0,
            'reputation_score': 100,
            'blacklisted': False,
            'points': 0,
            'level': 1,
            'created_at': datetime.now().isoformat()
        }

        response = requests.post(
            f"{SHARED_API_URL}/users",
            json=data,
            headers=HEADERS,
            timeout=5
        )

        if response.status_code == 200:
            logger.info(f"创建用户档案: {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"创建用户档案失败: {e}")
        return False


async def update_user(user_id: int, data: dict):
    """更新用户信息"""
    try:
        response = requests.post(
            f"{SHARED_API_URL}/users",
            json={'user_id': user_id, **data},
            headers=HEADERS,
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"更新用户信息失败: {e}")
        return False
