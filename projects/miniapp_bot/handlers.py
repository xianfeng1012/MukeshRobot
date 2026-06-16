"""
MiniAppBot 事件处理器
积分/签到/排行榜的数据源为 yanyulou 项目 API（与小程序内积分一致）
群聊中签到/查询类命令的命令与回复会在 2 分钟后自动删除，避免刷屏。
"""
import logging
import time
import html
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import (
    MINIAPP_URL, YANYULOU_API_BASE, YANYULOU_API_KEY, LEADERBOARD_SIZE,
    YANYULOU_TMA_BASE, BOT_USERNAME,
    CHANNEL_FEATURED, CHANNEL_PART_TIME, CHANNEL_NEWBIE,
)

logger = logging.getLogger(__name__)

# 分类 → 中文标签 / 频道
CATEGORY_LABEL = {'FEATURED': '精品', 'PART_TIME': '兼职', 'NEWBIE': '新生'}
CATEGORY_CHANNEL = {
    'FEATURED': CHANNEL_FEATURED,
    'PART_TIME': CHANNEL_PART_TIME,
    'NEWBIE': CHANNEL_NEWBIE,
}

# 群聊中命令/回复自动删除的延时（秒）
AUTO_DELETE_SECONDS = 120

# 用户昵称缓存（减少 getChat 调用）: user_id -> (name, expire_ts)
_name_cache = {}
_NAME_TTL = 600  # 秒


# ============ 群聊自动删除（防刷屏） ============
async def _delete_later(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_ids: list):
    """延时后删除指定消息"""
    await asyncio.sleep(AUTO_DELETE_SECONDS)
    for mid in message_ids:
        try:
            await context.bot.delete_message(chat_id, mid)
        except Exception:
            pass


def _schedule_delete(update: Update, context: ContextTypes.DEFAULT_TYPE, *messages):
    """群聊中：安排 2 分钟后删除用户命令消息 + 机器人回复（私聊不删）"""
    chat = update.effective_chat
    if chat is None or chat.type == 'private':
        return
    ids = []
    if update.message:
        ids.append(update.message.message_id)
    for m in messages:
        if m is not None:
            ids.append(m.message_id)
    if ids:
        context.application.create_task(_delete_later(context, chat.id, ids))


async def reply_clean(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    """发送回复，并在群聊中安排 2 分钟后自动删除（命令+回复）"""
    sent = await update.message.reply_text(text, **kwargs)
    _schedule_delete(update, context, sent)
    return sent


# ============ yanyulou API 调用 ============
def yanyulou_api(method: str, path: str, data: dict = None):
    """调用 yanyulou 项目 API，失败返回 None"""
    url = YANYULOU_API_BASE + path
    headers = {
        'X-API-Key': YANYULOU_API_KEY,
        'Content-Type': 'application/json',
    }
    try:
        resp = requests.request(method, url, json=data, headers=headers, timeout=8)
        if resp.status_code == 200:
            return resp.json()
        logger.warning(f"yanyulou API {path} -> {resp.status_code}: {resp.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"yanyulou API 调用失败 {path}: {e}")
        return None


def _get_rank(user_id: int) -> str:
    """从排行榜中找出该用户的名次文本"""
    rank = yanyulou_api('GET', '/api/bot/rank?limit=50')
    if isinstance(rank, list):
        for r in rank:
            if str(r.get('telegramId')) == str(user_id):
                return f"第{r.get('rank')}名"
    return "未上榜"


async def get_display_name(context: ContextTypes.DEFAULT_TYPE, user_id, fallback: str = None) -> str:
    """从 Telegram 获取用户姓名（昵称：first_name + last_name），带缓存与回退"""
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return fallback or f"用户{user_id}"

    cached = _name_cache.get(uid)
    if cached and cached[1] > time.time():
        return cached[0]

    name = None
    try:
        chat = await context.bot.get_chat(uid)
        name = chat.first_name or ''
        if chat.last_name:
            name = f"{name} {chat.last_name}".strip()
        name = name or None
    except Exception as e:
        logger.warning(f"获取用户{uid}昵称失败: {e}")

    name = name or fallback or f"用户{uid}"
    _name_cache[uid] = (name, time.time() + _NAME_TTL)
    return name


# ============ 积分查询 ============
async def cmd_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查询用户积分（来自 yanyulou）"""
    try:
        user_id = update.effective_user.id

        data = yanyulou_api('GET', f'/api/bot/points/{user_id}')
        if data is None:
            await reply_clean(update, context, "❌ 获取积分失败，请稍后重试")
            return

        points = data.get('points', 0)
        streak = data.get('streak', 0)

        await reply_clean(
            update, context,
            f"💰 *你的积分信息*\n\n"
            f"总积分: `{points}`\n"
            f"连续签到: `{streak}` 天\n"
            f"排名: `{_get_rank(user_id)}`",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"查询积分失败: {e}")
        await reply_clean(update, context, f"❌ 查询失败: {e}")


# ============ 排行榜 ============
async def cmd_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示排行榜（来自 yanyulou）"""
    try:
        leaderboard = yanyulou_api('GET', f'/api/bot/rank?limit={LEADERBOARD_SIZE}')
        if not isinstance(leaderboard, list):
            await reply_clean(update, context, "❌ 获取排行榜失败")
            return

        if not leaderboard:
            await reply_clean(update, context, "🏆 排行榜暂时还没有数据")
            return

        message = "🏆 *积分排行榜 (Top 10)*\n\n"
        medal = ['🥇', '🥈', '🥉']
        for r in leaderboard:
            idx = r.get('rank', 0)
            points = r.get('points', 0)
            name = await get_display_name(context, r.get('telegramId'), fallback=r.get('name'))
            medal_str = medal[idx - 1] if 1 <= idx <= 3 else f"{idx}."
            message += f"{medal_str} {name}: `{points}` 分\n"

        await reply_clean(update, context, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取排行榜失败: {e}")
        await reply_clean(update, context, f"❌ 获取失败: {e}")


# ============ 打开 Mini App ============
async def cmd_play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """打开小程序（直链到 t.me 小程序，不自动删除）"""
    try:
        buttons = [[InlineKeyboardButton(text="🎮 打开小程序", url=MINIAPP_URL)]]
        await update.message.reply_text(
            "🎮 点击下方按钮打开小程序 👇\n\n"
            "在小程序中你可以:\n"
            "✅ 完成任务赚取积分\n"
            "✅ 查看个人成就\n"
            "✅ 参与排行榜\n"
            "✅ 获取奖励",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        logger.info(f"用户{update.effective_user.id}打开小程序")

    except Exception as e:
        logger.error(f"打开小程序失败: {e}")
        await update.message.reply_text(f"❌ 打开失败: {e}")


# ============ 每日签到 ============
async def cmd_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """每日签到（调用 yanyulou 签到接口，与小程序共用同一套签到/连续天数）"""
    try:
        user_id = update.effective_user.id

        result = yanyulou_api('POST', '/api/bot/sign-in', {'telegramId': user_id})
        if result is None:
            await reply_clean(update, context, "❌ 签到失败，请稍后重试")
            return

        # yanyulou 返回的 message 已是用户友好文案（含已签到/连续天数/获得积分）
        message = result.get('message') or ("✅ 签到成功！" if result.get('success') else "签到失败")
        await reply_clean(update, context, message)
        logger.info(f"用户{user_id}签到: success={result.get('success')}")

    except Exception as e:
        logger.error(f"签到失败: {e}")
        await reply_clean(update, context, f"❌ 签到失败: {e}")


# ============ 任务列表 ============
async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示任务/玩法"""
    try:
        message = (
            "📋 *任务 & 玩法*\n\n"
            "📅 *每日签到* `/checkin`\n"
            "   首次签到 `10` 分，连续签到递增（最高 `22` 分/天）\n\n"
            "🎮 *打开小程序* `/play`\n"
            "   更多任务、解锁、成就尽在小程序\n\n"
            "🏆 *积分排行* `/leaderboard`\n"
            "💰 *查看积分* `/points`"
        )
        await reply_clean(update, context, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        await reply_clean(update, context, f"❌ 获取失败: {e}")


# ============ 个人统计 ============
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看个人统计（来自 yanyulou）"""
    try:
        user_id = update.effective_user.id

        data = yanyulou_api('GET', f'/api/bot/points/{user_id}')
        if data is None:
            await reply_clean(update, context, "❌ 获取统计失败")
            return

        points = data.get('points', 0)
        streak = data.get('streak', 0)
        name = update.effective_user.full_name

        message = (
            f"📊 *{name} 的个人统计*\n\n"
            f"💰 总积分: `{points}`\n"
            f"🔥 连续签到: `{streak}` 天\n"
            f"📈 当前排名: `{_get_rank(user_id)}`"
        )
        await reply_clean(update, context, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        await reply_clean(update, context, f"❌ 获取失败: {e}")


# ============ 频道发布：把人物资料发到对应频道 ============
def _build_profile_caption(p: dict, with_anchor: bool = True) -> str:
    """资料文案（HTML，段落之间空一行）。with_anchor=True 时末尾附 📖 文字超链接（频道用）。"""
    def esc(s):
        return html.escape(str(s))

    label = CATEGORY_LABEL.get(p.get('category'), '')
    blocks = []

    # 标题：🌸 名称 · 分类
    title = f"🌸 {esc(p.get('name', ''))}"
    if label:
        title += f" · {label}"
    blocks.append(title)

    # 📍 地区 · 区域 · 年龄 · 身高
    info = []
    if p.get('region'):
        info.append(esc(p['region']))
    if p.get('location'):
        info.append(esc(p['location']))
    if p.get('age'):
        info.append(f"{esc(p['age'])}岁")
    if p.get('heightCm'):
        info.append(f"{esc(p['heightCm'])}cm")
    if info:
        blocks.append("📍 " + " · ".join(info))

    # 🎯 服务（为空不显示）
    services = [s for s in (p.get('servicesList') or []) if s]
    if services:
        blocks.append("🎯 " + "、".join(esc(s) for s in services))

    # 💰 价格（只显示非空项）
    prices = []
    if p.get('priceP'):
        prices.append(f"P:{esc(p['priceP'])}")
    if p.get('pricePP'):
        prices.append(f"PP:{esc(p['pricePP'])}")
    if p.get('priceBY'):
        prices.append(f"BY:{esc(p['priceBY'])}")
    if prices:
        blocks.append("💰 " + " / ".join(prices))

    # ⭐ 评分（无人评价不显示）
    if p.get('ratingCount'):
        blocks.append(f"⭐ {esc(p.get('ratingAvg', 0))} ({esc(p['ratingCount'])})")

    # 简介
    if p.get('bio'):
        blocks.append(esc(str(p['bio'])[:200]))

    # 状态：ACTIVE→可预约 / HIDDEN→休息中
    if p.get('status') == 'HIDDEN':
        blocks.append("🔴 休息中")
    else:
        blocks.append("✅ 可预约")

    # 锚文本（文字超链接，跳转到机器人私聊）——仅频道帖使用
    if with_anchor:
        link = f"https://t.me/{BOT_USERNAME}?start=girl_{p.get('id')}"
        blocks.append(f'<a href="{link}">📖 查看资料/联系方式/评论</a>')

    return "\n\n".join(blocks)[:1024]


def _build_media(images, caption):
    """构造相册媒体列表，仅首图带说明(HTML)"""
    return [
        InputMediaPhoto(
            media=url,
            caption=caption if i == 0 else None,
            parse_mode=ParseMode.HTML if i == 0 else None,
        )
        for i, url in enumerate(images)
    ]


async def publish_profile_to_channel(bot, p: dict) -> dict:
    """发布资料到对应分类频道（单条多图相册）。
    已发布过：同频道且图片数量一致 → 就地编辑；否则删旧帖重发。
    返回 {success, channelId, messageIds(逗号分隔)}。"""
    category = p.get('category')
    channel = CATEGORY_CHANNEL.get(category)
    if not channel:
        logger.error(f"未知分类，无法发布: {category}")
        return {'success': False, 'message': f'未知分类: {category}'}
    if not p.get('id'):
        return {'success': False, 'message': '缺少资料ID'}

    images = [u for u in (p.get('images') or []) if u][:10]
    if not images and p.get('avatarUrl'):
        images = [p['avatarUrl']]
    if not images:
        return {'success': False, 'message': '该资料没有图片，无法发布'}

    caption = _build_profile_caption(p)
    timeouts = dict(read_timeout=60, write_timeout=60, connect_timeout=20)

    # 解析旧帖位置
    old_channel = None
    try:
        if p.get('tgChannelId'):
            old_channel = int(p['tgChannelId'])
    except (TypeError, ValueError):
        old_channel = None
    old_ids = [int(x) for x in str(p.get('tgChannelMsgId') or '').split(',') if x.strip().isdigit()]

    # 情形1：已发布、同频道、同图片数量 → 就地编辑
    if old_ids and old_channel == channel and len(old_ids) == len(images):
        try:
            for i, (mid, url) in enumerate(zip(old_ids, images)):
                try:
                    await bot.edit_message_media(
                        chat_id=channel, message_id=mid,
                        media=InputMediaPhoto(
                            media=url,
                            caption=caption if i == 0 else None,
                            parse_mode=ParseMode.HTML if i == 0 else None,
                        ),
                        **timeouts
                    )
                except Exception as ie:
                    # 该图与说明都没变化时 Telegram 返回 "message is not modified"，跳过即可
                    if 'not modified' in str(ie).lower():
                        continue
                    raise
            logger.info(f"资料 {p['id']} 已就地编辑频道帖 {channel} {old_ids}")
            return {'success': True, 'message': '已更新频道帖子',
                    'channelId': str(channel), 'messageIds': ','.join(map(str, old_ids))}
        except Exception as e:
            logger.warning(f"就地编辑失败，转为删旧重发: {e}")

    # 情形2：旧帖存在但无法编辑（频道/数量变化或编辑失败）→ 删旧
    if old_ids:
        for mid in old_ids:
            try:
                await bot.delete_message(chat_id=(old_channel or channel), message_id=mid)
            except Exception:
                pass

    # 情形3：发新帖
    try:
        if len(images) == 1:
            sent = await bot.send_photo(
                chat_id=channel, photo=images[0], caption=caption,
                parse_mode=ParseMode.HTML, **timeouts
            )
            new_ids = [sent.message_id]
        else:
            sent = await bot.send_media_group(
                chat_id=channel, media=_build_media(images, caption), **timeouts
            )
            new_ids = [m.message_id for m in sent]
    except Exception as e:
        logger.error(f"发布资料 {p.get('id')} 到频道 {channel} 失败: {e}")
        return {'success': False, 'message': str(e)}

    logger.info(f"资料 {p['id']} 已发布到频道 {channel} {new_ids}")
    return {'success': True, 'message': '已发布到频道',
            'channelId': str(channel), 'messageIds': ','.join(map(str, new_ids))}


async def send_girl_teaser(update: Update, context: ContextTypes.DEFAULT_TYPE, girl_id: str):
    """用户从频道跳转私聊后，发送该资料的头图+简介 + 打开小程序按钮（定位到该资料）"""
    data = yanyulou_api('GET', f'/api/bot/girls/{girl_id}')
    if not isinstance(data, dict) or not data.get('name'):
        await update.message.reply_text("😅 资料获取失败，可能已下架。")
        return

    images = data.get('images') or []
    header = images[0] if images else None

    # 与频道帖保持一致的文案格式（不带末尾锚文本，改用下方按钮跳小程序）
    p = {
        'id': girl_id,
        'name': data.get('name'),
        'category': data.get('category'),
        'status': data.get('status'),
        'region': data.get('city'),
        'location': data.get('location'),
        'age': data.get('age'),
        'heightCm': data.get('heightCm'),
        'servicesList': data.get('servicesList'),
        'priceP': data.get('priceP'),
        'pricePP': data.get('pricePP'),
        'priceBY': data.get('priceBY'),
        'ratingAvg': data.get('ratingAvg'),
        'ratingCount': data.get('ratingCount'),
        'bio': data.get('bio'),
    }
    caption = _build_profile_caption(p, with_anchor=False)

    button = InlineKeyboardButton(
        "🔎 查看资料/联系方式/评论",
        web_app=WebAppInfo(url=f"{YANYULOU_TMA_BASE}/girls/{girl_id}")
    )
    kb = InlineKeyboardMarkup([[button]])

    if header:
        await update.message.reply_photo(photo=header, caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=kb)
    logger.info(f"已向用户 {update.effective_user.id} 推送资料 {girl_id}")
