import html
import re
from typing import Optional

from telegram import Chat, ChatPermissions, Message, Update, User
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

from MukeshRobot import TIGERS, WOLVES, dispatcher
from MukeshRobot.modules.connection import connected
from MukeshRobot.modules.helper_funcs.alternate import send_message
from MukeshRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from MukeshRobot.modules.helper_funcs.string_handling import extract_time
from MukeshRobot.modules.log_channel import loggable
from MukeshRobot.modules.sql import antiflood_sql as sql
from MukeshRobot.modules.sql.approve_sql import is_approved

FLOOD_GROUP = 3


@loggable
def check_flood(update, context) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]
    if not user:  # ignore channels
        return ""

    # ignore admins and whitelists
    if is_user_admin(chat, user.id) or user.id in WOLVES or user.id in TIGERS:
        sql.update_flood(chat.id, None)
        return ""
    # ignore approved users
    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return
    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            chat.ban_member(user.id)
            execstrings = "已封禁"
            tag = "BANNED"
        elif getmode == 2:
            chat.ban_member(user.id)
            chat.unban_member(user.id)
            execstrings = "已踢出"
            tag = "KICKED"
        elif getmode == 3:
            context.bot.restrict_chat_member(
                chat.id, user.id, permissions=ChatPermissions(can_send_messages=False)
            )
            execstrings = "已禁言"
            tag = "MUTED"
        elif getmode == 4:
            bantime = extract_time(msg, getvalue)
            chat.kick_member(user.id, until_date=bantime)
            execstrings = "封禁 {}".format(getvalue)
            tag = "TBAN"
        elif getmode == 5:
            mutetime = extract_time(msg, getvalue)
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "禁言 {}".format(getvalue)
            tag = "TMUTE"
        send_message(
            update.effective_message, "正在刷屏！\n{}！".format(execstrings)
        )

        return (
            "<b>{}:</b>"
            "\n#{}"
            "\n<b>用户:</b> {}"
            "\n在群组中刷屏。".format(
                tag,
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
            )
        )

    except BadRequest:
        msg.reply_text(
            "我无法在此群限制用户 🚫，请先给我相应权限，否则我将禁用防刷屏功能。"
        )
        sql.set_flood(chat.id, 0)
        return (
            "<b>{}:</b>"
            "\n#INFO"
            "\n权限不足，无法限制用户，已自动禁用防刷屏。".format(
                chat.title
            )
        )


@user_admin_no_reply
@bot_admin
def flood_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"unmute_flooder\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat.id
        try:
            bot.restrict_chat_member(
                chat,
                int(user_id),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            update.effective_message.edit_text(
                f"已由 ♥︎{mention_html(user.id, html.escape(user.first_name))} 解除禁言。",
                parse_mode="HTML",
            )
        except:
            pass


@user_admin
@loggable
def set_flood(update, context) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "此命令只能在群组中使用，不能在私聊中使用",
            )
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val in ["off", "no", "0"]:
            sql.set_flood(chat_id, 0)
            if conn:
                text = message.reply_text(
                    "已在 {} 中禁用防刷屏。".format(chat_name)
                )
            else:
                text = message.reply_text("防刷屏已禁用。")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    text = message.reply_text(
                        "已在 {} 中禁用防刷屏。".format(chat_name)
                    )
                else:
                    text = message.reply_text("防刷屏已禁用。")
                return (
                    "<b>{}:</b>"
                    "\n#SETFLOOD"
                    "\n<b>管理员:</b> {}"
                    "\n已禁用防刷屏。".format(
                        html.escape(chat_name),
                        mention_html(user.id, html.escape(user.first_name)),
                    )
                )

            elif amount <= 3:
                send_message(
                    update.effective_message,
                    "防刷屏上限必须为 0（禁用）或大于 3 的数字！",
                )
                return ""

            else:
                sql.set_flood(chat_id, amount)
                if conn:
                    text = message.reply_text(
                        "已在群组 {} 中将防刷屏设置为 {} 条消息。".format(
                            chat_name, amount
                        )
                    )
                else:
                    text = message.reply_text(
                        "防刷屏已设置为 {} 条消息。".format(amount)
                    )
                return (
                    "<b>{}:</b>"
                    "\n#SETFLOOD"
                    "\n<b>管理员:</b> {}"
                    "\n已将防刷屏设置为 <code>{}</code> 条消息。".format(
                        html.escape(chat_name),
                        mention_html(user.id, html.escape(user.first_name)),
                        amount,
                    )
                )

        else:
            message.reply_text("参数无效，请使用数字、'off' 或 'no'")
    else:
        message.reply_text(
            (
                "使用 `/setflood 数量` 来开启防刷屏。\n或使用 `/setflood off` 来关闭防刷屏。"
            ),
            parse_mode="markdown",
        )
    return ""


def flood(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "此命令只能在群组中使用，不能在私聊中使用",
            )
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            text = msg.reply_text(
                "群组 {} 尚未开启防刷屏！".format(chat_name)
            )
        else:
            text = msg.reply_text("此群尚未开启防刷屏。")
    else:
        if conn:
            text = msg.reply_text(
                "当前在群组 {} 中，连续发送 {} 条消息后将受到限制。".format(
                    chat_name, limit
                )
            )
        else:
            text = msg.reply_text(
                "当前连续发送 {} 条消息后将受到限制。".format(
                    limit
                )
            )


@user_admin
def set_flood_mode(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "此命令只能在群组中使用，不能在私聊中使用",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == "ban":
            settypeflood = "封禁"
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == "kick":
            settypeflood = "踢出"
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeflood = "禁言"
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """看起来你尝试为防刷屏设置时间值，但未指定时间；请尝试 `/setfloodmode tban <时间值>`。
时间值示例：4m = 4 分钟，3h = 3 小时，6d = 6 天，5w = 5 周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "临时封禁 {}".format(args[1])
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = (
                    update.effective_message,
                    """看起来你尝试为防刷屏设置时间值，但未指定时间；请尝试 `/setfloodmode tmute <时间值>`。
时间值示例：4m = 4 分钟，3h = 3 小时，6d = 6 天，5w = 5 周。""",
                )
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "临时禁言 {}".format(args[1])
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            send_message(
                update.effective_message, "仅支持 ban/kick/mute/tban/tmute！"
            )
            return
        if conn:
            text = msg.reply_text(
                "超过刷屏上限后，将对用户执行{}操作（群组：{}）！".format(
                    settypeflood, chat_name
                )
            )
        else:
            text = msg.reply_text(
                "超过刷屏上限后，将对用户执行{}操作！".format(
                    settypeflood
                )
            )
        return (
            "<b>{}:</b>\n"
            "<b>管理员:</b> {}\n"
            "已更改刷屏处罚方式，将对用户执行{}。".format(
                settypeflood,
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
            )
        )
    else:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            settypeflood = "封禁"
        elif getmode == 2:
            settypeflood = "踢出"
        elif getmode == 3:
            settypeflood = "禁言"
        elif getmode == 4:
            settypeflood = "临时封禁 {}".format(getvalue)
        elif getmode == 5:
            settypeflood = "临时禁言 {}".format(getvalue)
        if conn:
            text = msg.reply_text(
                "超过刷屏上限后，将在群组 {} 中对用户执行{}操作。".format(
                    chat_name, settypeflood
                )
            )
        else:
            text = msg.reply_text(
                "超过刷屏上限后，将对用户执行{}操作。".format(
                    settypeflood
                )
            )
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "尚未开启防刷屏。"
    else:
        return "防刷屏已设置为 `{}` 条消息。".format(limit)


__help__ = """
 ❍ /flood*:* 获取当前防刷屏设置

*仅管理员:*
 ❍ /setflood <数量/关闭>*:* 开启或关闭刷屏控制。设置为 0 或 'off' 表示关闭。
 ❍ /setfloodmode <封禁/踢出/禁言/tban/tmute> <时间值>*:* 设置达到刷屏上限后的处罚方式。
"""

__mod_name__ = "防刷屏"

FLOOD_BAN_HANDLER = MessageHandler(
    Filters.all & ~Filters.status_update & Filters.chat_type.groups,
    check_flood,
    run_async=True,
)
SET_FLOOD_HANDLER = CommandHandler(
    "setflood", set_flood, filters=Filters.chat_type.groups, run_async=True
)

SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode", set_flood_mode, pass_args=True, run_async=True
)  # , filters=Filters.chat_type.groups)
FLOOD_QUERY_HANDLER = CallbackQueryHandler(
    flood_button, pattern=r"unmute_flooder", run_async=True
)
FLOOD_HANDLER = CommandHandler(
    "flood", flood, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
dispatcher.add_handler(FLOOD_QUERY_HANDLER)
dispatcher.add_handler(SET_FLOOD_HANDLER)
dispatcher.add_handler(SET_FLOOD_MODE_HANDLER)
dispatcher.add_handler(FLOOD_HANDLER)

__handlers__ = [
    (FLOOD_BAN_HANDLER, FLOOD_GROUP),
    SET_FLOOD_HANDLER,
    FLOOD_HANDLER,
    SET_FLOOD_MODE_HANDLER,
]
