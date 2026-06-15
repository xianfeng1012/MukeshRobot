import html
import re

from telegram import ChatPermissions, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html

import MukeshRobot.modules.sql.blacklist_sql as sql
from MukeshRobot import LOGGER, dispatcher
from MukeshRobot.modules.connection import connected
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.alternate import send_message, typing_action
from MukeshRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from MukeshRobot.modules.helper_funcs.extraction import extract_text
from MukeshRobot.modules.helper_funcs.misc import split_message
from MukeshRobot.modules.helper_funcs.string_handling import extract_time
from MukeshRobot.modules.log_channel import loggable
from MukeshRobot.modules.sql.approve_sql import is_approved
from MukeshRobot.modules.warns import warn

BLACKLIST_GROUP = 11


@user_admin
@typing_action
def blacklist(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    filter_list = "<b>{}</b> 的黑名单词语：\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    # for trigger in all_blacklisted:
    #     filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "<b>{}</b> 的黑名单词语：\n".format(
            html.escape(chat_name)
        ):
            send_message(
                update.effective_message,
                "<b>{}</b> 暂无黑名单词语！".format(html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@user_admin
@typing_action
def add_blacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        for trigger in to_blacklist:
            sql.add_to_blacklist(chat_id, trigger.lower())

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "已在 <b>{}</b> 中添加黑名单触发词 <code>{}</code>！".format(
                    html.escape(chat_name), html.escape(to_blacklist[0])
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "已在 <b>{}</b> 中添加 <code>{}</code> 个黑名单触发词！".format(
                    html.escape(chat_name), len(to_blacklist)
                ),
                parse_mode=ParseMode.HTML,
            )

    else:
        send_message(
            update.effective_message,
            "请告诉我你想添加到黑名单的词语。",
        )


@user_admin
@typing_action
def unblacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "已从 <b>{}</b> 的黑名单中移除 <code>{}</code>！".format(
                        html.escape(chat_name), html.escape(to_unblacklist[0])
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message, "该词语不在黑名单中！"
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "已从 <b>{}</b> 的黑名单中移除 <code>{}</code> 个触发词！".format(
                    html.escape(chat_name), successful
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "这些触发词均不在黑名单中，无法移除。",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "已移除 <code>{}</code> 个触发词，另有 {} 个不在黑名单中，未能移除。".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )
    else:
        send_message(
            update.effective_message,
            "请告诉我你想从黑名单中移除的词语！",
        )


@loggable
@user_admin
@typing_action
def blacklist_mode(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
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
                "此命令只能在群组中使用，不能在私聊中使用。",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "不执行操作"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "删除黑名单消息"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "警告发送者"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "禁言发送者"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "踢出发送者"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "封禁发送者"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """看起来你想为黑名单设置临时封禁时长，但未指定时间，请使用 `/blacklistmode tban <时间值>`。

时间值示例：4m = 4分钟，3h = 3小时，6d = 6天，5w = 5周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """时间值无效！
时间值示例：4m = 4分钟，3h = 3小时，6d = 6天，5w = 5周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "临时封禁 {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """看起来你想为黑名单设置临时禁言时长，但未指定时间，请使用 `/blacklistmode tmute <时间值>`。

时间值示例：4m = 4分钟，3h = 3小时，6d = 6天，5w = 5周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """时间值无效！
时间值示例：4m = 4分钟，3h = 3小时，6d = 6天，5w = 5周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "临时禁言 {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "仅支持以下选项：off/del/warn/ban/kick/mute/tban/tmute！",
            )
            return ""
        if conn:
            text = "已将 *{}* 的黑名单处罚方式设为：`{}`！".format(
                chat_name, settypeblacklist
            )
        else:
            text = "已将黑名单处罚方式设为：`{}`！".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>管理员：</b> {}\n"
            "已修改黑名单处罚方式，将执行：{}。".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "不执行操作"
        elif getmode == 1:
            settypeblacklist = "删除"
        elif getmode == 2:
            settypeblacklist = "警告"
        elif getmode == 3:
            settypeblacklist = "禁言"
        elif getmode == 4:
            settypeblacklist = "踢出"
        elif getmode == 5:
            settypeblacklist = "封禁"
        elif getmode == 6:
            settypeblacklist = "临时封禁 {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "临时禁言 {}".format(getvalue)
        if conn:
            text = "*{}* 当前黑名单处罚方式：*{}*。".format(
                chat_name, settypeblacklist
            )
        else:
            text = "当前黑名单处罚方式：*{}*。".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


@user_not_admin
def del_blacklist(update, context):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot = context.bot
    to_match = extract_text(message)
    if not to_match:
        return
    if is_approved(chat.id, user.id):
        return
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    try:
                        message.delete()
                    except BadRequest:
                        pass
                elif getmode == 2:
                    try:
                        message.delete()
                    except BadRequest:
                        pass
                    warn(
                        update.effective_user,
                        chat,
                        ("使用了黑名单触发词：{}".format(trigger)),
                        message,
                        update.effective_user,
                    )
                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"已禁言 {user.first_name}，原因：使用了黑名单词语：{trigger}！",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            f"已踢出 {user.first_name}，原因：使用了黑名单词语：{trigger}！",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.ban_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        f"已封禁 {user.first_name}，原因：使用了黑名单词语：{trigger}",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.ban_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        f"已临时封禁 {user.first_name} 至 '{value}'，原因：使用了黑名单词语：{trigger}！",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        until_date=mutetime,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"已临时禁言 {user.first_name} 至 '{value}'，原因：使用了黑名单词语：{trigger}！",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "Message to delete not found":
                    LOGGER.exception("Error while deleting blacklist message.")
            break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("blacklist", {})
    for trigger in blacklist:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "共有 {} 个黑名单词语。".format(blacklisted)


def __stats__():
    return "• {} 个黑名单触发词，分布在 {} 个群组中。".format(
        sql.num_blacklist_filters(), sql.num_blacklist_filter_chats()
    )


__mod_name__ = "黑名单"

__help__ = """
 ❍ /blacklist*:* 查看当前黑名单词语

*仅管理员:*
 ❍ /addblacklist <触发词>*:* 将词语添加到黑名单。每行一个词。
 ❍ /unblacklist <触发词>*:* 从黑名单中移除词语。每行一个词。
 ❍ /blacklistmode <关闭/删除/警告/禁言/踢出/封禁/封禁贴纸>*:* 设置命中黑名单时的处罚方式。默认为删除。
"""

BLACKLIST_HANDLER = DisableAbleCommandHandler(
    "blacklist", blacklist, pass_args=True, admin_ok=True, run_async=True
)
ADD_BLACKLIST_HANDLER = CommandHandler("addblacklist", add_blacklist, run_async=True)
UNBLACKLIST_HANDLER = CommandHandler("unblacklist", unblacklist, run_async=True)
BLACKLISTMODE_HANDLER = CommandHandler(
    "blacklistmode", blacklist_mode, pass_args=True, run_async=True
)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo)
    & Filters.chat_type.groups,
    del_blacklist,
    allow_edit=True,
    run_async=True,
)

dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__handlers__ = [
    BLACKLIST_HANDLER,
    ADD_BLACKLIST_HANDLER,
    UNBLACKLIST_HANDLER,
    BLACKLISTMODE_HANDLER,
    (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP),
]
