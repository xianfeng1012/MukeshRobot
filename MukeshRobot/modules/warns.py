import html
import re
from typing import Optional

import telegram
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    DispatcherHandlerStop,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

from MukeshRobot import TIGERS, WOLVES, dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from MukeshRobot.modules.helper_funcs.extraction import (
    extract_text,
    extract_user,
    extract_user_and_text,
)
from MukeshRobot.modules.helper_funcs.filters import CustomFilters
from MukeshRobot.modules.helper_funcs.misc import split_message
from MukeshRobot.modules.helper_funcs.string_handling import split_quotes
from MukeshRobot.modules.log_channel import loggable
from MukeshRobot.modules.sql import warns_sql as sql
from MukeshRobot.modules.sql.approve_sql import is_approved

WARN_HANDLER_GROUP = 9
CURRENT_WARNING_FILTER_STRING = "<b>本群当前的警告过滤器：</b>\n"


# Not async
def warn(
    user: User,
    chat: Chat,
    reason: str,
    message: Message,
    warner: User = None,
) -> str:
    if is_user_admin(chat, user.id):
        # message.reply_text("Damn admins, They are too far to be One Punched!")
        return

    if user.id in TIGERS:
        if warner:
            message.reply_text("虎级用户不能被警告。")
        else:
            message.reply_text(
                "虎级用户触发了自动警告过滤器！\n我不能警告虎级用户，但他们应该避免滥用这一点。",
            )
        return

    if user.id in WOLVES:
        if warner:
            message.reply_text("狼级灾害免疫警告。")
        else:
            message.reply_text(
                "狼级灾害触发了自动警告过滤器！\n我不能警告狼级用户，但他们应该避免滥用这一点。",
            )
        return

    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "自动警告过滤器。"

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # punch
            chat.unban_member(user.id)
            reply = (
                f"<code>❕</code><b>踢出事件</b>\n"
                f"<code> </code><b>•  用户：</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>•  警告次数：</b> {limit}"
            )

        else:  # ban
            chat.kick_member(user.id)
            reply = (
                f"<code>❕</code><b>封禁事件</b>\n"
                f"<code> </code><b>•  用户：</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>•  警告次数：</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        # message.bot.send_sticker(chat.id, BAN_STICKER)
        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN_BAN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✨ ʀᴇᴍᴏᴠᴇ ✨",
                        callback_data="rm_warn({})".format(user.id),
                    ),
                ],
            ],
        )

        reply = (
            f"<code>❕</code><b>警告事件</b>\n"
            f"<code> </code><b>•  用户：</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>•  警告次数：</b> {num_warns}/{limit}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  原因：</b> {html.escape(reason)}"

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#WARN\n"
            f"<b>Admin:</b> {warner_tag}\n"
            f"<b>User:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>Reason:</b> {reason}\n"
            f"<b>Counts:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        message.reply_text(reply, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                reply,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                quote=False,
            )
        else:
            raise
    return log_reason



@user_admin_no_reply
@bot_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_warn\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        res = sql.remove_warn(user_id, chat.id)
        if res:
            update.effective_message.edit_text(
                "警告已由 {} 移除。".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )
            user_member = chat.get_member(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNWARN\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
            )
        else:
            update.effective_message.edit_text(
                "该用户已经没有任何警告记录。",
                parse_mode=ParseMode.HTML,
            )

    return ""


@user_admin
@can_restrict
@loggable
def warn_user(update: Update, context: CallbackContext) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    warner: Optional[User] = update.effective_user

    user_id, reason = extract_user_and_text(message, args)
    if message.text.startswith("/d") and message.reply_to_message:
        message.reply_to_message.delete()
    if user_id:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return warn(
                message.reply_to_message.from_user,
                chat,
                reason,
                message.reply_to_message,
                warner,
            )
        else:
            return warn(chat.get_member(user_id).user, chat, reason, message, warner)
    else:
        message.reply_text("这看起来是一个无效的用户 ID。")
    return ""


@user_admin
@bot_admin
@loggable
def reset_warns(update: Update, context: CallbackContext) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user

    user_id = extract_user(message, args)

    if user_id:
        sql.reset_warns(user_id, chat.id)
        message.reply_text("警告次数已重置！")
        warned = chat.get_member(user_id).user
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#RESETWARNS\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(warned.id, warned.first_name)}"
        )
    else:
        message.reply_text("未指定任何用户！")
    return ""


def warns(update: Update, context: CallbackContext):
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = extract_user(message, args) or update.effective_user.id
    result = sql.get_warns(user_id, chat.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(chat.id)

        if reasons:
            text = (
                f"该用户有 {num_warns}/{limit} 次警告，原因如下："
            )
            for reason in reasons:
                text += f"\n • {reason}"

            msgs = split_message(text)
            for msg in msgs:
                update.effective_message.reply_text(msg)
        else:
            update.effective_message.reply_text(
                f"该用户有 {num_warns}/{limit} 次警告，但均未注明原因。",
            )
    else:
        update.effective_message.reply_text("该用户没有任何警告记录！")


# Dispatcher handler stop - do not async
@user_admin
def add_warn_filter(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None,
        1,
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) >= 2:
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()
        content = extracted[1]

    else:
        return

    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in dispatcher.handlers.get(WARN_HANDLER_GROUP, []):
        if handler.filters == (keyword, chat.id):
            dispatcher.remove_handler(handler, WARN_HANDLER_GROUP)

    sql.add_warn_filter(chat.id, keyword, content)

    update.effective_message.reply_text(f"已为关键词 '{keyword}' 添加警告触发器！")
    raise DispatcherHandlerStop


@user_admin
def remove_warn_filter(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None,
        1,
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        return

    to_remove = extracted[0]

    chat_filters = sql.get_chat_warn_triggers(chat.id)

    if not chat_filters:
        msg.reply_text("此处没有任何活跃的警告过滤器！")
        return

    for filt in chat_filters:
        if filt == to_remove:
            sql.remove_warn_filter(chat.id, to_remove)
            msg.reply_text("好的，我将不再对此关键词发出警告。")
            raise DispatcherHandlerStop

    msg.reply_text(
        "这不是当前的警告过滤器 - 使用 /warnlist 查看所有活跃的警告过滤器。",
    )


def list_warn_filters(update: Update, context: CallbackContext):
    chat: Optional[Chat] = update.effective_chat
    all_handlers = sql.get_chat_warn_triggers(chat.id)

    if not all_handlers:
        update.effective_message.reply_text("此处没有任何活跃的警告过滤器！")
        return

    filter_list = CURRENT_WARNING_FILTER_STRING
    for keyword in all_handlers:
        entry = f" - {html.escape(keyword)}\n"
        if len(entry) + len(filter_list) > telegram.MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)
            filter_list = entry
        else:
            filter_list += entry

    if filter_list != CURRENT_WARNING_FILTER_STRING:
        update.effective_message.reply_text(filter_list, parse_mode=ParseMode.HTML)


@loggable
def reply_filter(update: Update, context: CallbackContext) -> str:
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message
    user: Optional[User] = update.effective_user

    if not user:  # Ignore channel
        return

    if user.id == 777000:
        return
    if is_approved(chat.id, user.id):
        return
    chat_warn_filters = sql.get_chat_warn_triggers(chat.id)
    to_match = extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user: Optional[User] = update.effective_user
            warn_filter = sql.get_warn_filter(chat.id, keyword)
            return warn(user, chat, warn_filter.reply, message)
    return ""


@user_admin
@loggable
def set_warn_limit(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].isdigit():
            if int(args[0]) < 3:
                msg.reply_text("警告上限最少为 3！")
            else:
                sql.set_warn_limit(chat.id, int(args[0]))
                msg.reply_text("警告上限已更新为 {}".format(args[0]))
                return (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#SET_WARN_LIMIT\n"
                    f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                    f"将警告上限设置为 <code>{args[0]}</code>"
                )
        else:
            msg.reply_text("请提供一个数字作为参数！")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)

        msg.reply_text("当前警告上限为 {}".format(limit))
    return ""


@user_admin
def set_warn_strength(update: Update, context: CallbackContext):
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(chat.id, False)
            msg.reply_text("警告次数过多将导致封禁！")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"已启用强力警告。用户将被封禁。"
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_warn_strength(chat.id, True)
            msg.reply_text(
                "警告次数过多将导致踢出！用户之后可以重新加入。",
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"已禁用强力警告。将对用户使用踢出处罚。"
            )

        else:
            msg.reply_text("我只接受 on/yes/no/off！")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        if soft_warn:
            msg.reply_text(
                "当前设置为超过警告上限时*踢出*用户。",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            msg.reply_text(
                "当前设置为超过警告上限时*封禁*用户。",
                parse_mode=ParseMode.MARKDOWN,
            )
    return ""


def __stats__():
    return (
        f"• {sql.num_warns()} ᴏᴠᴇʀᴀʟʟ ᴡᴀʀɴs, ᴀᴄʀᴏss {sql.num_warn_chats()} ᴄʜᴀᴛs.\n"
        f"• {sql.num_warn_filters()} ᴡᴀʀɴ ғɪʟᴛᴇʀs, ᴀᴄʀᴏss {sql.num_warn_filter_chats()} ᴄʜᴀᴛs."
    )


def __import_data__(chat_id, data):
    for user_id, count in data.get("warns", {}).items():
        for x in range(int(count)):
            sql.warn_user(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = sql.num_warn_chat_filters(chat_id)
    limit, soft_warn = sql.get_warn_setting(chat_id)
    return (
        f"本群共有 `{num_warn_filters}` 个警告过滤器。"
        f"用户触发 `{limit}` 次警告后将被*{'踢出' if soft_warn else '封禁'}*。"
    )


__help__ = """
*仅管理员:*
 ❍ /warn <用户名>*:* 警告用户。累计到警告上限后将自动处罚。
 ❍ /dwarn <用户名>*:* 警告用户并删除触发警告的消息。
 ❍ /resetwarn <用户名>*:* 重置用户的警告次数。
 ❍ /addwarn <关键词> <回复内容>*:* 设置触发词，命中时自动发出警告。
 ❍ /nowarn <关键词>*:* 停止对某关键词的警告。
 ❍ /warnlimit <数量>*:* 设置警告上限。
 ❍ /strongwarn <开/关>*:* 开启时，超过警告上限将封禁而非踢出。
 ❍ /warns <用户名>*:* 查看某用户的警告次数及原因。
 ❍ /warnlist*:* 列出所有自动警告触发词。
"""

__mod_name__ = "警告"

WARN_HANDLER = CommandHandler(
    ["warn", "dwarn"], warn_user, filters=Filters.chat_type.groups, run_async=True
)
RESET_WARN_HANDLER = CommandHandler(
    ["resetwarn", "resetwarns"],
    reset_warns,
    filters=Filters.chat_type.groups,
    run_async=True,
)
CALLBACK_QUERY_HANDLER = CallbackQueryHandler(
    button, pattern=r"rm_warn", run_async=True
)
MYWARNS_HANDLER = DisableAbleCommandHandler(
    "warns", warns, filters=Filters.chat_type.groups, run_async=True
)
ADD_WARN_HANDLER = CommandHandler(
    "addwarn", add_warn_filter, filters=Filters.chat_type.groups, run_async=True
)

RM_WARN_HANDLER = CommandHandler(
    ["nowarn", "stopwarn"],
    remove_warn_filter,
    filters=Filters.chat_type.groups,
    run_async=True,
)
LIST_WARN_HANDLER = DisableAbleCommandHandler(
    ["warnlist", "warnfilters"],
    list_warn_filters,
    filters=Filters.chat_type.groups,
    admin_ok=True,
    run_async=True,
)
WARN_FILTER_HANDLER = MessageHandler(
    CustomFilters.has_text & Filters.chat_type.groups,
    reply_filter,
    run_async=True,
)
WARN_LIMIT_HANDLER = CommandHandler(
    "warnlimit", set_warn_limit, filters=Filters.chat_type.groups, run_async=True
)
WARN_STRENGTH_HANDLER = CommandHandler(
    "strongwarn",
    set_warn_strength,
    filters=Filters.chat_type.groups,
    run_async=True,
)

dispatcher.add_handler(WARN_HANDLER)
dispatcher.add_handler(CALLBACK_QUERY_HANDLER)
dispatcher.add_handler(RESET_WARN_HANDLER)
dispatcher.add_handler(MYWARNS_HANDLER)
dispatcher.add_handler(ADD_WARN_HANDLER)
dispatcher.add_handler(RM_WARN_HANDLER)
dispatcher.add_handler(LIST_WARN_HANDLER)
dispatcher.add_handler(WARN_LIMIT_HANDLER)
dispatcher.add_handler(WARN_STRENGTH_HANDLER)
dispatcher.add_handler(WARN_FILTER_HANDLER, WARN_HANDLER_GROUP)
