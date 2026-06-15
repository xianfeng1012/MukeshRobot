import html
import os
import re

import requests
from telegram import (
    MAX_MESSAGE_LENGTH,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.messageentity import MessageEntity
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import escape_markdown, mention_html
from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins
from MukeshRobot.modules.alive import Mukesh
import MukeshRobot.modules.sql.userinfo_sql as sql
from MukeshRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    INFOPIC,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
    telethn,
    BOT_NAME,
    BOT_USERNAME
)

from MukeshRobot.__main__ import STATS, TOKEN, USER_INFO
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.chat_status import sudo_plus
from MukeshRobot.modules.helper_funcs.extraction import extract_user
from MukeshRobot.modules.sql.global_bans_sql import is_user_gbanned
from MukeshRobot.modules.sql.users_sql import get_user_num_chats


def no_by_per(totalhp, percentage):
    """
    rtype: num of `percentage` from total
    eg: 1000, 10 -> 10% of 1000 (100)
    """
    return totalhp * percentage / 100


def get_percentage(totalhp, earnedhp):
    """
    rtype: percentage of `totalhp` num
    eg: (1000, 100) will return 10%
    """

    matched_less = totalhp - earnedhp
    per_of_totalhp = 100 - matched_less * 100.0 / totalhp
    per_of_totalhp = str(int(per_of_totalhp))
    return per_of_totalhp


def hpmanager(user):
    total_hp = (get_user_num_chats(user.id) + 10) * 10

    if not is_user_gbanned(user.id):

        # Assign new var `new_hp` since we need `total_hp` in
        # end to calculate percentage.
        new_hp = total_hp

        # if no username decrease 25% of hp.
        if not user.username:
            new_hp -= no_by_per(total_hp, 25)
        try:
            dispatcher.bot.get_user_profile_photos(user.id).photos[0][-1]
        except IndexError:
            # no profile photo ==> -25% of hp
            new_hp -= no_by_per(total_hp, 25)
        # if no /setme exist ==> -20% of hp
        if not sql.get_user_me_info(user.id):
            new_hp -= no_by_per(total_hp, 20)
        # if no bio exsit ==> -10% of hp
        if not sql.get_user_bio(user.id):
            new_hp -= no_by_per(total_hp, 10)


        # fbanned users will have (2*number of fbans) less from max HP
        # Example: if HP is 100 but user has 5 diff fbans
        # Available HP is (2*5) = 10% less than Max HP
        # So.. 10% of 100HP = 90HP

    # Commenting out fban health decrease cause it wasnt working and isnt needed ig.
    # _, fbanlist = get_user_fbanlist(user.id)
    # new_hp -= no_by_per(total_hp, 2 * len(fbanlist))

    # Bad status effects:
    # gbanned users will always have 5% HP from max HP
    # Example: If HP is 100 but gbanned
    # Available HP is 5% of 100 = 5HP

    else:
        new_hp = no_by_per(total_hp, 5)

    return {
        "earnedhp": int(new_hp),
        "totalhp": int(total_hp),
        "percentage": get_percentage(total_hp, new_hp),
    }


def make_bar(per):
    done = min(round(per / 10), 10)
    return "■" * done + "□" * (10 - done)


def get_id(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    msg = update.effective_message
    user_id = extract_user(msg, args)

    if user_id:

        if msg.reply_to_message and msg.reply_to_message.forward_from:

            user1 = message.reply_to_message.from_user
            user2 = message.reply_to_message.forward_from

            msg.reply_text(
                f"<b>Telegram ID：</b>\n"
                f"• {html.escape(user2.first_name)} - <code>{user2.id}</code>\n"
                f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>",
                parse_mode=ParseMode.HTML,
            )

        else:

            user = bot.get_chat(user_id)
            msg.reply_text(
                f"{html.escape(user.first_name)} 的 ID 是 <code>{user.id}</code>。",
                parse_mode=ParseMode.HTML,
            )

    else:

        if chat.type == "private":
            msg.reply_text(
                f"你的用户 ID 是 <code>{chat.id}</code>。", parse_mode=ParseMode.HTML
            )

        else:
            msg.reply_text(
                f"本群组的 ID 是 <code>{chat.id}</code>。", parse_mode=ParseMode.HTML
            )


@telethn.on(
    events.NewMessage(
        pattern="/ginfo",from_users=(TIGERS or []) + (DRAGONS or []) + (DEMONS or [])
    ),
)
async def group_info(event) -> None:
    chat = event.text.split(" ", 1)[1]
    try:
        entity = await event.client.get_entity(chat)
        totallist = await event.client.get_participants(
            entity, filter=ChannelParticipantsAdmins
        )
        ch_full = await event.client(GetFullChannelRequest(channel=entity))
    except:
        await event.reply(
            "无法获取信息，可能该群组是私密群组，或我已被封禁。"
        )
        return
    msg = f"**ID**: `{entity.id}`"
    msg += f"\n**名称**: `{entity.title}`"
    msg += f"\n**DC**: `{entity.photo.dc_id}`"
    msg += f"\n**视频头像**: `{entity.photo.has_video}`"
    msg += f"\n**超级群组**: `{entity.megagroup}`"
    msg += f"\n**受限**: `{entity.restricted}`"
    msg += f"\n**诈骗标记**: `{entity.scam}`"
    msg += f"\n**慢速模式**: `{entity.slowmode_enabled}`"
    if entity.username:
        msg += f"\n**用户名**: @{entity.username}"
    msg += "\n\n**成员统计：**"
    msg += f"\n管理员：`{len(totallist)}`"
    msg += f"\n成员：`{totallist.total}`"
    msg += "\n\n**管理员列表：**"
    for x in totallist:
        msg += f"\n• [{x.id}](tg://user?id={x.id})"
    msg += f"\n\n**简介**：\n`{ch_full.full_chat.about}`"
    await event.reply(msg)


def gifid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        update.effective_message.reply_text(
            f"GIF ID：\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text("请回复一个 GIF 以获取其 ID。")


def info(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = message.from_user

    elif not message.reply_to_message and (
        not args
        or (
            len(args) >= 1
            and not args[0].startswith("@")
            and not args[0].isdigit()
            and not message.parse_entities([MessageEntity.TEXT_MENTION])
        )
    ):
        message.reply_text("无法从该消息中提取用户信息。")
        return

    else:
        return

    rep = message.reply_text("<code>正在提取信息...</code>", parse_mode=ParseMode.HTML)

    text = (
        f"ㅤ ㅤㅤ      ✦ 用户信息 ✦\n•❅─────✧❅✦❅✧─────❅•\n"
        f"➻ <b>用户 ID：</b> <code>{user.id}</code>\n"
        f"➻ <b>名：</b> {html.escape(user.first_name)}"
    )

    if user.last_name:
        text += f"\n➻ <b>姓：</b> {html.escape(user.last_name)}"

    if user.username:
        text += f"\n➻ <b>用户名：</b> @{html.escape(user.username)}"

    text += f"\n➻ <b>链接：</b> {mention_html(user.id, '链接')}"

    if chat.type != "private" and user_id != bot.id:
        _stext = "\n➻ <b>状态：</b> <code>{}</code>"

        status = status = bot.get_chat_member(chat.id, user.id).status
        if status:
            if status in {"left", "kicked"}:
                text += _stext.format("不在群内")
            elif status == "member":
                text += _stext.format("成员")
            elif status in {"administrator", "creator"}:
                text += _stext.format("管理员")
    if user_id not in [bot.id, 777000, 1087968824]:
        userhp = hpmanager(user)
        text += f"\n\n<b>生命值：</b> <code>{userhp['earnedhp']}/{userhp['totalhp']}</code>\n[<i>{make_bar(int(userhp['percentage']))} </i>{userhp['percentage']}%]"

    disaster_level_present = False

    if user.id == OWNER_ID:
        text += "\n\n该用户的灾难等级为 <b>神</b>。\n"
        disaster_level_present = True
    elif user.id in DEV_USERS:
        text += "\n\n该用户是 <b>Mukesh 协会</b> 的成员。\n"
        disaster_level_present = True
    elif user.id in DRAGONS:
        text += "\n\n该用户的灾难等级为 <b>龙</b>。\n"
        disaster_level_present = True
    elif user.id in DEMONS:
        text += "\n\n该用户的灾难等级为 <b>恶魔</b>。\n"
        disaster_level_present = True
    elif user.id in TIGERS:
        text += "\n\n该用户的灾难等级为 <b>虎</b>。\n"
        disaster_level_present = True
    elif user.id in WOLVES:
        text += "\n\n该用户的灾难等级为 <b>狼</b>。\n"
        disaster_level_present = True

    if disaster_level_present:
        text += ' \n[<a href="https://t.me/mukeshbotzone/26">点击此处了解灾难等级。</a>]'.format(
            bot.username
        )

    try:
        user_member = chat.get_member(user.id)
        if user_member.status == "administrator":
            result = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat.id}&user_id={user.id}"
            )
            result = result.json()["result"]
            if "custom_title" in result.keys():
                custom_title = result["custom_title"]
                text += f"\n\n头衔：\n<b>{custom_title}</b>"
    except BadRequest:
        pass

   

    if INFOPIC:
        try:
            profile = context.bot.get_user_profile_photos(user.id).photos[0][-1]
            _file = bot.get_file(profile["file_id"])
            _file.download(f"{user.id}.png")

            message.reply_photo(
                photo=open(f"{user.id}.png", "rb"),
                caption=(text),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "生命值", url=f"https://t.me/mukeshbotzone/90"
                            ),
                            InlineKeyboardButton(
                                "灾难等级", url="https://t.me/mukeshbotzone/26"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="➕将我添加到你的群组➕",
                                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                            ),
                        ],
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )

            os.remove(f"{user.id}.png")
        # Incase user don't have profile pic, send normal text
        except IndexError:
            message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "生命值", url="https://t.me/mukeshbotzone/90"
                            ),
                            InlineKeyboardButton(
                                "灾难等级", url="https://t.me/mukeshbotzone/26"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="➕将我添加到你的群组➕",
                                url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                            ),
                        ],
                    ]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
    else:
        message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
        )

    rep.delete()


def about_me(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user_id = extract_user(message, args)

    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text(
            f"*{user.first_name}*:\n{escape_markdown(info)}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(
            f"{username} 还没有设置个人简介！"
        )
    else:
        update.effective_message.reply_text("你还没有设置个人简介，使用 /setme 来设置。")


def set_about_me(update: Update, context: CallbackContext):
    message = update.effective_message
    user_id = message.from_user.id
    if user_id in [777000, 1087968824]:
        message.reply_text("ᴇʀʀᴏʀ ᴜɴᴀᴜᴛʜᴏʀɪsᴇᴅ")
        return
    bot = context.bot
    if message.reply_to_message:
        repl_message = message.reply_to_message
        repl_user_id = repl_message.from_user.id
        if repl_user_id in [bot.id, 777000, 1087968824] and (user_id in DEV_USERS):
            user_id = repl_user_id
    text = message.text
    info = text.split(None, 1)
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            if user_id in [777000, 1087968824]:
                message.reply_text("已授权……信息已更新！")
            elif user_id == bot.id:
                message.reply_text("我已用你提供的内容更新了我的信息！")
            else:
                message.reply_text("信息已更新！")
        else:
            message.reply_text(
                "信息需要少于 {} 个字符！你输入了 {} 个字符。".format(
                    MAX_MESSAGE_LENGTH // 4, len(info[1])
                )
            )


def stats(update: Update, context: CallbackContext):
    stats = f"<b> ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛs ᴏғ {BOT_NAME} :</b>\n" + "\n".join(
        [mod.__stats__() for mod in STATS]
    )
    result = re.sub(r"(\d+)", r"<code>\1</code>", stats)
    update.effective_message.reply_text(result, parse_mode=ParseMode.HTML)


def about_bio(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    user_id = extract_user(message, args)
    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(
            f"{username} 还没有设置简介！\n使用 /setbio 来设置。"
        )
    else:
        update.effective_message.reply_text(
            "你还没有设置简介！"
        )


def set_about_bio(update: Update, context: CallbackContext):
    message = update.effective_message
    sender_id = update.effective_user.id
    bot = context.bot

    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id

        if user_id == message.from_user.id:
            message.reply_text(
                "哈，你不能自己给自己设置简介！这里需要别人来给你写。"
            )
            return

        if user_id in [777000, 1087968824] and sender_id not in DEV_USERS:
            message.reply_text("你没有权限执行此操作。")
            return

        if user_id == bot.id and sender_id not in DEV_USERS:
            message.reply_text(
                "嗯……我只信任 Mukesh 协会的成员来设置我的简介。"
            )
            return

        text = message.text
        bio = text.split(
            None, 1
        )  # use python's maxsplit to only remove the cmd, hence keeping newlines.

        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text(
                    "已更新 {} 的简介！".format(repl_message.from_user.first_name)
                )
            else:
                message.reply_text(
                    "简介需要少于 {} 个字符！你输入了 {} 个字符。".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])
                    )
                )
    else:
        message.reply_text("请回复某个用户来设置他们的简介！")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    result = ""
    if me:
        result += f"<b>个人介绍：</b>\n{me}\n"
    if bio:
        result += f"<b>他人评价：</b>\n{bio}\n"
    result = result.strip("\n")
    return result


__help__ = """
*ID 相关：*
 ❍ /id*：* 获取当前群组的 ID。如果用于回复某条消息，则获取该用户的 ID。
 ❍ /gifid *：* 回复一个 GIF，获取其文件 ID。

*自填信息：*
 ❍ /setme <文本>*：* 设置你的个人介绍
 ❍ /me *：* 获取你或其他用户的个人介绍。
*示例：* 💡
 ➩ /setme 我是一匹狼。
 ➩ /me @username（不指定用户则默认显示自己）

*他人对你的描述：*
 ❍ /bio *：* 获取你或其他用户的简介。此内容不能由本人设置。
 ❍ /setbio <文本>*：* 回复某用户时使用，将保存对方的简介。
*示例：* 💡
 ➩ /bio @username（不指定用户则默认显示自己）`
 ➩ /setbio 这个用户是一匹狼`（回复目标用户）

*关于你的综合信息：*
 ❍ /info *：* 获取某用户的详细信息。
 ❍ /myinfo *：* 显示发送该命令的用户的信息。
"""

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio, run_async=True)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio, run_async=True)

STATS_HANDLER = CommandHandler("stats", stats, run_async=True)
ID_HANDLER = DisableAbleCommandHandler("id", get_id, run_async=True)
GIFID_HANDLER = DisableAbleCommandHandler("gifid", gifid, run_async=True)
INFO_HANDLER = DisableAbleCommandHandler(("info", "book"), info, run_async=True)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me, run_async=True)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me, run_async=True)

dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(GIFID_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)

__mod_name__ = "用户信息"
__command_list__ = ["setbio", "bio", "setme", "me", "info"]
__handlers__ = [
    ID_HANDLER,
    GIFID_HANDLER,
    INFO_HANDLER,
    SET_BIO_HANDLER,
    GET_BIO_HANDLER,
    SET_ABOUT_HANDLER,
    GET_ABOUT_HANDLER,
    STATS_HANDLER,
]
