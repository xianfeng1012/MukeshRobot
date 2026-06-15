"""
GroupBot 事件处理器
"""
import logging
import requests
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ContextTypes

from config import (
    SHARED_API_URL, API_BOT_TOKEN, VERIFICATION_TIMEOUT, VERIFICATION_TEXT,
    MAX_VIOLATIONS, VIOLATION_TIMEOUT, SPAM_FILTER_ENABLED, AD_KEYWORDS
)

logger = logging.getLogger(__name__)

# API请求头
HEADERS = {
    'X-Bot-Token': API_BOT_TOKEN,
    'Content-Type': 'application/json'
}


# ============ 新成员加入处理 ============
async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理新成员加入"""
    try:
        new_members = update.message.new_chat_members
        chat = update.effective_chat

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

            # 3. 发送欢迎消息
            welcome_msg = await context.bot.send_message(
                chat.id,
                VERIFICATION_TEXT.format(user=member.first_name)
            )

            # 4. 发送验证按钮
            buttons = [[InlineKeyboardButton(
                text="✅ 我是真人",
                callback_data=f"verify_{user_id}"
            )]]

            verify_msg = await context.bot.send_message(
                chat.id,
                f"{member.mention_html()}，请点击下方按钮验证",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

            # 5. 限制用户权限
            await context.bot.restrict_chat_member(
                chat.id,
                user_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                )
            )

            # 6. 设置超时（120秒后检查是否验证）
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
        data = job.context

        chat_id = data['chat_id']
        user_id = data['user_id']
        message_id = data['message_id']

        # 检查用户是否已验证
        user = await get_user(user_id)
        if user and user.get('verified'):
            return

        # 未验证，踢出用户
        await context.bot.ban_chat_member(chat_id, user_id)
        await context.bot.delete_message(chat_id, message_id)

        logger.warning(f"用户{user_id}验证超时，已踢出")

    except Exception as e:
        logger.error(f"验证超时处理失败: {e}")


# ============ 验证按钮处理 ============
async def handle_verification_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理验证按钮点击"""
    try:
        query = update.callback_query
        user_id = int(query.data.split('_')[1])
        chat_id = query.message.chat_id

        # 检查点击用户是否与加入用户一致
        if query.from_user.id != user_id:
            await query.answer("❌ 你无权执行此操作", show_alert=True)
            return

        # 标记为已验证
        await update_user(user_id, {'verified': True})

        # 解除限制
        await context.bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )

        # 删除验证消息
        try:
            await query.message.delete()
        except:
            pass

        await query.answer("✅ 验证成功！欢迎加入！", show_alert=False)
        logger.info(f"用户{user_id}验证成功")

        # 取消超时任务
        try:
            context.job_queue.get_jobs_by_name(f'verify_timeout_{user_id}')[0].schedule_removal()
        except:
            pass

    except Exception as e:
        logger.error(f"处理验证按钮失败: {e}")


# ============ 消息过滤 ============
async def filter_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """实时垃圾消息过滤"""
    try:
        if not SPAM_FILTER_ENABLED:
            return

        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user

        # 跳过管理员和系统消息
        if not message.text:
            return

        chat_admins = await context.bot.get_chat_administrators(chat.id)
        admin_ids = [admin.user.id for admin in chat_admins]

        if user.id in admin_ids:
            return

        # 检查广告关键词
        text = message.text.lower()
        for keyword in AD_KEYWORDS:
            if keyword in text:
                await message.delete()

                # 增加违规计数
                user_data = await get_user(user.id)
                violations = user_data.get('violations', 0) if user_data else 0
                violations += 1

                await update_user(user.id, {'violations': violations})

                # 如果违规超过限制，禁言
                if violations >= MAX_VIOLATIONS:
                    await context.bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        permissions=ChatPermissions(
                            can_send_messages=False
                        ),
                        until_date=datetime.now() + timedelta(seconds=VIOLATION_TIMEOUT)
                    )

                    await context.bot.send_message(
                        chat.id,
                        f"⚠️ 用户 {user.mention_html()} 因多次违规已被禁言24小时",
                        parse_mode=ParseMode.HTML
                    )

                    logger.warning(f"用户{user.id}因多次违规被禁言")
                else:
                    await context.bot.send_message(
                        chat.id,
                        f"⚠️ {user.mention_html()}，请不要发送广告内容\n"
                        f"违规次数: {violations}/{MAX_VIOLATIONS}",
                        parse_mode=ParseMode.HTML
                    )

                logger.info(f"删除垃圾消息: 用户{user.id}, 内容包含关键词")
                break

    except Exception as e:
        logger.error(f"过滤垃圾消息失败: {e}")


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
