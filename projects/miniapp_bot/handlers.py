"""
MiniAppBot 事件处理器
积分/签到/排行榜的数据源为 yanyulou 项目 API（与小程序内积分一致）
群聊中签到/查询类命令的命令与回复会在 2 分钟后自动删除，避免刷屏。
"""
import logging
import time
import html
import asyncio
from datetime import datetime, timezone, timedelta
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import (
    MINIAPP_URL, YANYULOU_API_BASE, YANYULOU_API_KEY, LEADERBOARD_SIZE,
    YANYULOU_TMA_BASE, BOT_USERNAME,
    CHANNEL_FEATURED, CHANNEL_PART_TIME, CHANNEL_NEWBIE,
    CHANNEL_LINK_FEATURED, CHANNEL_LINK_PART_TIME, CHANNEL_LINK_NEWBIE,
    SCHEDULE_CITY, SCHEDULE_CHANNEL_ID,
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


# ============ 管理员限制（斜杠命令群内仅管理员可用） ============
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
                return  # 非管理员的斜杠命令，群内无效
        await handler(update, context)
    return wrapped


async def reply_plain(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, **kwargs):
    """普通回复，不安排自动删除（汉字命令用，保留成员发言）"""
    return await update.message.reply_text(text, **kwargs)


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
async def cmd_points(update: Update, context: ContextTypes.DEFAULT_TYPE, clean: bool = True):
    """查询用户积分（来自 yanyulou）"""
    reply = reply_clean if clean else reply_plain
    try:
        user_id = update.effective_user.id

        data = yanyulou_api('GET', f'/api/bot/points/{user_id}')
        if data is None:
            await reply(update, context, "❌ 获取积分失败，请稍后重试")
            return

        points = data.get('points', 0)
        streak = data.get('streak', 0)

        await reply(
            update, context,
            f"💰 *你的积分信息*\n\n"
            f"总积分: `{points}`\n"
            f"连续签到: `{streak}` 天\n"
            f"排名: `{_get_rank(user_id)}`",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"查询积分失败: {e}")
        await reply(update, context, f"❌ 查询失败: {e}")


# ============ 排行榜 ============
async def cmd_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, clean: bool = True):
    """显示排行榜（来自 yanyulou）"""
    reply = reply_clean if clean else reply_plain
    try:
        leaderboard = yanyulou_api('GET', f'/api/bot/rank?limit={LEADERBOARD_SIZE}')
        if not isinstance(leaderboard, list):
            await reply(update, context, "❌ 获取排行榜失败")
            return

        if not leaderboard:
            await reply(update, context, "🏆 排行榜暂时还没有数据")
            return

        message = "🏆 *积分排行榜 (Top 10)*\n\n"
        medal = ['🥇', '🥈', '🥉']
        for r in leaderboard:
            idx = r.get('rank', 0)
            points = r.get('points', 0)
            name = await get_display_name(context, r.get('telegramId'), fallback=r.get('name'))
            medal_str = medal[idx - 1] if 1 <= idx <= 3 else f"{idx}."
            message += f"{medal_str} {name}: `{points}` 分\n"

        await reply(update, context, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取排行榜失败: {e}")
        await reply(update, context, f"❌ 获取失败: {e}")


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
async def _checkin_core(update: Update, context: ContextTypes.DEFAULT_TYPE, clean: bool):
    """签到核心逻辑。clean=True 时群内 2 分钟自动删除命令+回复；False 则保留成员发言。"""
    try:
        user_id = update.effective_user.id
        result = yanyulou_api('POST', '/api/bot/sign-in', {'telegramId': user_id})
        if result is None:
            text = "❌ 签到失败，请稍后重试"
        else:
            # yanyulou 返回的 message 已是用户友好文案（含已签到/连续天数/获得积分）
            text = result.get('message') or ("✅ 签到成功！" if result.get('success') else "签到失败")
            logger.info(f"用户{user_id}签到: success={result.get('success')}")

        if clean:
            await reply_clean(update, context, text)
        else:
            await update.message.reply_text(text)
    except Exception as e:
        logger.error(f"签到失败: {e}")
        await update.message.reply_text(f"❌ 签到失败: {e}")


async def cmd_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/checkin 斜杠命令（群内仅管理员，命令+回复2分钟自动删除）"""
    await _checkin_core(update, context, clean=True)


async def text_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """汉字「签到」（所有群友可用，保留成员发言不删除）"""
    await _checkin_core(update, context, clean=False)


# ============ 任务列表 ============
async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE, clean: bool = True):
    """显示任务/玩法"""
    reply = reply_clean if clean else reply_plain
    try:
        message = (
            "📋 *任务 & 玩法*\n\n"
            "📅 每日签到：发送「签到」\n"
            "   首次签到 `10` 分，连续签到递增（最高 `22` 分/天）\n\n"
            "🎮 打开小程序：发送「小程序」\n"
            "   更多任务、解锁、成就尽在小程序\n\n"
            "🏆 积分排行：发送「排行榜」\n"
            "💰 查看积分：发送「积分」"
        )
        await reply(update, context, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        await reply(update, context, f"❌ 获取失败: {e}")


# ============ 个人统计 ============
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, clean: bool = True):
    """查看个人统计（来自 yanyulou）"""
    reply = reply_clean if clean else reply_plain
    try:
        user_id = update.effective_user.id

        data = yanyulou_api('GET', f'/api/bot/points/{user_id}')
        if data is None:
            await reply(update, context, "❌ 获取统计失败")
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
        await reply(update, context, message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        await reply(update, context, f"❌ 获取失败: {e}")


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


# ============ 今日开课（列出在线资料） ============
# 「今日开课」只展示「精品」和「新生」，不展示「兼职」
SCHEDULE_CATEGORIES = [('FEATURED', '精品'), ('NEWBIE', '新生')]


def _build_schedule_text(girls: list) -> str:
    """把 ACTIVE 资料渲染成「今日开课」文本（HTML）。仅含本群城市、精品/新生。"""
    def esc(s):
        return html.escape(str(s))

    # 仅保留本群城市（成都群只列成都）
    city_girls = [g for g in girls if SCHEDULE_CITY in (g.get('city') or '')]

    # 北京时间日期
    today = datetime.now(timezone(timedelta(hours=8))).strftime('%Y/%m/%d')
    city_name = next((g.get('city') for g in city_girls if g.get('city')), f'{SCHEDULE_CITY}市')

    # 按 分类 → 位置 分组（保留接口返回顺序：createdAt desc）
    total = 0
    cat_blocks = []
    for cat_key, cat_label in SCHEDULE_CATEGORIES:
        members = [g for g in city_girls if g.get('category') == cat_key]
        if not members:
            continue
        total += len(members)

        loc_order = []
        loc_map = {}
        for g in members:
            loc = (g.get('location') or '其他').strip() or '其他'
            if loc not in loc_map:
                loc_map[loc] = []
                loc_order.append(loc)
            link = f"https://t.me/{BOT_USERNAME}?start=girl_{g.get('id')}"
            loc_map[loc].append(f'<a href="{link}">{esc(g.get("name", ""))}</a>')

        loc_blocks = []
        for loc in loc_order:
            loc_blocks.append(f"📍 {esc(loc)}\n" + " | ".join(loc_map[loc]))
        cat_blocks.append(f"<b>{cat_label}</b>\n\n" + "\n\n".join(loc_blocks))

    if total == 0:
        header = f"📋 【{esc(city_name)}】今日开课老师 ({today})"
        return header + "\n\n🟢 暂无可开课老师，请稍后再看～"

    header = f"📋 【{esc(city_name)}】今日开课老师（👆上图） ({today})"
    body = f"🟢 可开课 ({total}位)\n\n" + "\n\n".join(cat_blocks)
    footer = "（点击可查看详情）\n好好学习，天天向上。更多课程信息请点击👇："
    return f"{header}\n\n{body}\n\n{footer}"


def _collect_schedule_photos(girls: list) -> list:
    """按 精品→新生 顺序收集本群城市 ACTIVE 资料的头像URL（兼职不取，无图跳过）。"""
    city_girls = [g for g in girls if SCHEDULE_CITY in (g.get('city') or '')]
    photos = []
    for cat_key, _ in SCHEDULE_CATEGORIES:
        for g in city_girls:
            if g.get('category') == cat_key and g.get('photo'):
                photos.append(g['photo'])
    return photos


def _schedule_keyboard() -> InlineKeyboardMarkup:
    """今日开课底部三个榜单按钮"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("精品榜", url=CHANNEL_LINK_FEATURED),
        InlineKeyboardButton("兼职榜", url=CHANNEL_LINK_PART_TIME),
        InlineKeyboardButton("新生榜", url=CHANNEL_LINK_NEWBIE),
    ]])


def _has_active_teachers(girls: list) -> bool:
    """本群城市是否有 ACTIVE 的精品/新生老师"""
    return any(
        SCHEDULE_CITY in (g.get('city') or '') and g.get('category') in ('FEATURED', 'NEWBIE')
        for g in girls
    )


async def _send_schedule_albums(bot, chat_id, photos: list) -> list:
    """发送头像相册（每 10 张一组，Telegram 上限）。返回已发送的消息列表。"""
    sent = []
    for i in range(0, len(photos), 10):
        chunk = photos[i:i + 10]
        try:
            ms = await bot.send_media_group(
                chat_id, [InputMediaPhoto(media=u) for u in chunk],
                read_timeout=60, write_timeout=60, connect_timeout=20,
            )
            sent.extend(ms)
        except Exception as e:
            logger.error(f"发送今日开课相册失败: {e}")
    return sent


async def cmd_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE, clean: bool = True):
    """今日开课：先发头像相册，再发文本（带名字超链接+榜单按钮）。仅本群城市、精品/新生。"""
    girls = yanyulou_api('GET', '/api/bot/girls/active')
    if not isinstance(girls, list):
        reply = reply_clean if clean else reply_plain
        await reply(update, context, "❌ 获取开课信息失败，请稍后重试")
        return

    chat_id = update.effective_chat.id
    text = _build_schedule_text(girls)
    photos = _collect_schedule_photos(girls)

    sent_msgs = await _send_schedule_albums(context.bot, chat_id, photos)
    sent = await update.message.reply_text(
        text, parse_mode=ParseMode.HTML,
        reply_markup=_schedule_keyboard(), disable_web_page_preview=True,
    )
    sent_msgs.append(sent)

    # 群内 /schedule（clean=True）：相册+文本+命令一起 2 分钟后删除；汉字「今日开课」保留
    if clean:
        _schedule_delete(update, context, *sent_msgs)


async def publish_schedule_to_channel(context: ContextTypes.DEFAULT_TYPE):
    """每日定时任务：把「今日开课」同样的内容发布到公示榜频道（无 ACTIVE 老师则跳过）。"""
    bot = context.bot
    girls = yanyulou_api('GET', '/api/bot/girls/active')
    if not isinstance(girls, list):
        logger.error("定时发布：获取 active 资料失败，跳过")
        return
    if not _has_active_teachers(girls):
        logger.info("定时发布：今日无 ACTIVE 老师，跳过频道发布")
        return

    text = _build_schedule_text(girls)
    photos = _collect_schedule_photos(girls)
    await _send_schedule_albums(bot, SCHEDULE_CHANNEL_ID, photos)
    await bot.send_message(
        SCHEDULE_CHANNEL_ID, text, parse_mode=ParseMode.HTML,
        reply_markup=_schedule_keyboard(), disable_web_page_preview=True,
    )
    logger.info("定时发布：今日开课已发布到公示榜频道")


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
