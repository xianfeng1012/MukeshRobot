import html
from typing import Optional

from telegram import Chat, ChatPermissions, Message, ParseMode, Update, User
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html, mention_markdown

import MukeshRobot.modules.sql.blsticker_sql as sql
from MukeshRobot import LOGGER, dispatcher
from MukeshRobot.modules.connection import connected
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.alternate import send_message
from MukeshRobot.modules.helper_funcs.chat_status import user_admin, user_not_admin
from MukeshRobot.modules.helper_funcs.misc import split_message
from MukeshRobot.modules.helper_funcs.string_handling import extract_time
from MukeshRobot.modules.log_channel import loggable
from MukeshRobot.modules.warns import warn


def blackliststicker(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    sticker_list = "<b>{} 中当前的黑名单贴纸列表：</b>\n".format(
        chat_name
    )

    all_stickerlist = sql.get_chat_stickers(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_stickerlist:
            sticker_list += "<code>{}</code>\n".format(html.escape(trigger))
    elif len(args) == 0:
        for trigger in all_stickerlist:
            sticker_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(sticker_list)
    for text in split_text:
        if sticker_list == "<b>{} 中当前的黑名单贴纸列表：</b>\n".format(
            chat_name
        ).format(html.escape(chat_name)):
            send_message(
                update.effective_message,
                "<b>{}</b> 中暂无黑名单贴纸！".format(
                    html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )
            return
    send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@user_admin
def add_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = connected(bot, update, chat, user.id)
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
        text = words[1].replace("https://t.me/addstickers/", "")
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )

        added = 0
        for trigger in to_blacklist:
            try:
                bot.getStickerSet(trigger)
                sql.add_to_stickers(chat_id, trigger.lower())
                added += 1
            except BadRequest:
                send_message(
                    update.effective_message,
                    "找不到贴纸 `{}`！".format(trigger),
                    parse_mode="markdown",
                )

        if added == 0:
            return

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "贴纸 <code>{}</code> 已添加到 <b>{}</b> 的黑名单贴纸中！".format(
                    html.escape(to_blacklist[0]), html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            send_message(
                update.effective_message,
                "<code>{}</code> 个贴纸已添加到 <b>{}</b> 的黑名单中！".format(
                    added, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        added = 0
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "无效的贴纸！")
            return
        try:
            bot.getStickerSet(trigger)
            sql.add_to_stickers(chat_id, trigger.lower())
            added += 1
        except BadRequest:
            send_message(
                update.effective_message,
                "找不到贴纸 `{}`！".format(trigger),
                parse_mode="markdown",
            )

        if added == 0:
            return

        send_message(
            update.effective_message,
            "贴纸 <code>{}</code> 已添加到 <b>{}</b> 的黑名单贴纸中！".format(
                trigger, html.escape(chat_name)
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        send_message(
            update.effective_message,
            "请告诉我你想将哪些贴纸添加到黑名单中。",
        )


@user_admin
def unblackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = connected(bot, update, chat, user.id)
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
        text = words[1].replace("https://t.me/addstickers/", "")
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )

        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_stickers(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "贴纸 <code>{}</code> 已从 <b>{}</b> 的黑名单中移除！".format(
                        html.escape(to_unblacklist[0]), html.escape(chat_name)
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message, "该贴纸不在黑名单中！"
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "<code>{}</code> 个贴纸已从 <b>{}</b> 的黑名单中移除！".format(
                    successful, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "这些贴纸均不存在，无法移除。",
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "<code>{}</code> 个贴纸已从黑名单中移除，另有 {} 个不存在，未作处理。".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            send_message(update.effective_message, "无效的贴纸！")
            return
        success = sql.rm_from_stickers(chat_id, trigger.lower())

        if success:
            send_message(
                update.effective_message,
                "贴纸 <code>{}</code> 已从 <b>{}</b> 的黑名单中移除！".format(
                    trigger, chat_name
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            send_message(
                update.effective_message,
                "未在黑名单贴纸中找到 {}！".format(trigger),
            )
    else:
        send_message(
            update.effective_message,
            "请告诉我你想将哪些贴纸从黑名单中移除。",
        )


@loggable
@user_admin
def blacklist_mode(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    bot, args = context.bot, context.args
    conn = connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message, "该命令只能在群组中使用，不能在私聊中使用"
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "关闭"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "消息将被删除"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "警告"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "禁言"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "踢出"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "封禁"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """看起来你在尝试设置黑名单临时封禁，但未指定时长，请使用 `/blstickermode tban <时长>`。
                                          时长示例：4m = 4分钟，3h = 3小时，6d = 6天，5w = 5周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = "临时封禁 {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """看起来你在尝试设置黑名单临时禁言，但未指定时长，请使用 `/blstickermode tmute <时长>`。
                                          时长示例：4m = 4分钟，3h = 3小时，6d = 6天，5w = 5周。"""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeblacklist = "临时禁言 {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "只支持 off/del/warn/ban/kick/mute/tban/tmute！",
            )
            return
        if conn:
            text = "黑名单贴纸模式已更改，用户将被 `{}` 在 *{}*！".format(
                settypeblacklist, chat_name
            )
        else:
            text = "黑名单贴纸模式已更改，用户将被 `{}`！".format(
                settypeblacklist
            )
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>管理员：</b> {}\n"
            "已更改贴纸黑名单模式，用户将被 {}。".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "未启用"
        elif getmode == 1:
            settypeblacklist = "删除消息"
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
            text = "当前 *{}* 的黑名单贴纸模式设置为 *{}*。".format(
                chat_name, settypeblacklist
            )
        else:
            text = "当前黑名单贴纸模式设置为 *{}*。".format(
                settypeblacklist
            )
        send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


@user_not_admin
def del_blackliststicker(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user
    to_match = message.sticker
    if not to_match or not to_match.set_name:
        return
    bot = context.bot
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_stickers(chat.id)
    for trigger in chat_filters:
        if to_match.set_name.lower() == trigger.lower():
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    message.delete()
                elif getmode == 2:
                    message.delete()
                    warn(
                        update.effective_user,
                        chat,
                        "使用了黑名单贴纸 '{}'".format(
                            trigger
                        ),
                        message,
                        update.effective_user,
                        # conn=False,
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
                        "{} 因使用黑名单贴纸 '{}' 已被禁言".format(
                            mention_markdown(user.id, user.first_name), trigger
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            "{} 因使用黑名单贴纸 '{}' 已被踢出".format(
                                mention_markdown(user.id, user.first_name), trigger
                            ),
                            parse_mode="markdown",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.ban_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        "{} 因使用黑名单贴纸 '{}' 已被封禁".format(
                            mention_markdown(user.id, user.first_name), trigger
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.ban_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        "{} 因使用黑名单贴纸 '{}' 已被临时封禁 {}".format(
                            mention_markdown(user.id, user.first_name), trigger, value
                        ),
                        parse_mode="markdown",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=mutetime,
                    )
                    bot.sendMessage(
                        chat.id,
                        "{} 因使用黑名单贴纸 '{}' 已被临时禁言 {}".format(
                            mention_markdown(user.id, user.first_name), trigger, value
                        ),
                        parse_mode="markdown",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "Message to delete not found":
                    LOGGER.exception("Error while deleting blacklist message.")
                break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("sticker_blacklist", {})
    for trigger in blacklist:
        sql.add_to_stickers(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_stickers_chat_filters(chat_id)
    return "共有 `{}` 个黑名单贴纸。".format(blacklisted)


def __stats__():
    return "• {} ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs, ᴀᴄʀᴏss {} ᴄʜᴀᴛs.".format(
        sql.num_stickers_filters(), sql.num_stickers_filter_chats()
    )


__help__ = """
贴纸黑名单用于屏蔽特定贴纸包。一旦有人发送黑名单贴纸，消息将被立即处理。
*注意：* 贴纸黑名单不会对群组管理员生效。
 ❍ /blsticker*：* 查看当前黑名单贴纸列表
*仅管理员：*
 ❍ /addblsticker <贴纸链接>*：* 将贴纸添加到黑名单。也可以回复贴纸消息来添加
 ❍ /unblsticker <贴纸链接>*：* 从黑名单移除贴纸。支持换行批量移除多个贴纸
 ❍ /rmblsticker <贴纸链接>*：* 同上
 ❍ /blstickermode <ban/tban/mute/tmute>*：* 设置用户发送黑名单贴纸时的默认处罚方式
注意：
 ❍ <贴纸链接> 可以是 `https://t.me/addstickers/<贴纸>` 或直接输入 `<贴纸>` 名称，或者回复贴纸消息
"""

__mod_name__ = "贴纸黑名单"

BLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "blsticker", blackliststicker, admin_ok=True, run_async=True
)
ADDBLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "addblsticker", add_blackliststicker, run_async=True
)
UNBLACKLIST_STICKER_HANDLER = CommandHandler(
    ["unblsticker", "rmblsticker"], unblackliststicker, run_async=True
)

BLACKLISTMODE_HANDLER = CommandHandler("blstickermode", blacklist_mode)

BLACKLIST_STICKER_DEL_HANDLER = MessageHandler(
    Filters.sticker & Filters.chat_type.groups, del_blackliststicker, run_async=True
)

dispatcher.add_handler(BLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(ADDBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(UNBLACKLIST_STICKER_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_STICKER_DEL_HANDLER)
