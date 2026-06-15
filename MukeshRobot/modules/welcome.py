import html
import random
import re
import time
from contextlib import suppress
from functools import partial

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

import MukeshRobot
import MukeshRobot.modules.sql.welcome_sql as sql
from MukeshRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from MukeshRobot.modules.helper_funcs.chat_status import (
    is_user_ban_protected,
    user_admin,
)
from MukeshRobot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from MukeshRobot.modules.helper_funcs.msg_types import get_welcome_type
from MukeshRobot.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
)
from MukeshRobot.modules.log_channel import loggable
from MukeshRobot.modules.sql.global_bans_sql import is_user_gbanned

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}


# do not async
def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = update.message.message_id
    # Clean service welcome
    if cleanserv:
        try:
            dispatcher.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False
    try:
        msg = update.effective_message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            reply_to_message_id=reply,
        )
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            msg = update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                quote=False,
            )
        elif excp.message == "Button_url_invalid":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\n注意：当前消息的某个按钮包含无效链接，"
                    "请更新。"
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
        elif excp.message == "Unsupported url protocol":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\n注意：当前消息的按钮使用了 Telegram 不支持的链接协议，"
                    "请更新。"
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
        elif excp.message == "Wrong url host":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\n注意：当前消息包含一些无效链接，"
                    "请更新。"
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("Could not parse! got invalid url host errors")
        elif excp.message == "Have no rights to send a message":
            return
        else:
            msg = update.effective_message.reply_text(
                markdown_parser(
                    backup_message + "\n注意：发送自定义消息时出现错误，"
                    "请更新。"
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )
            LOGGER.exception()
    return msg


@loggable
def new_member(update: Update, context: CallbackContext):
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:

        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if should_welc:

            reply = update.message.message_id
            cleanserv = sql.clean_service(chat.id)
            # Clean service welcome
            if cleanserv:
                try:
                    dispatcher.bot.delete_message(chat.id, update.message.message_id)
                except BadRequest:
                    pass
                reply = False

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                update.effective_message.reply_text(
                    "哦，主人来了？让我们开始吧。", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#ᴜsᴇʀ_ᴊᴏɪɴᴇᴅ\n"
                    f"机器人主人刚刚加入了群组"
                )
                continue

            # Welcome Devs
            elif new_mem.id in DEV_USERS:
                update.effective_message.reply_text(
                    "保持冷静！英雄协会的成员刚刚加入。",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#ᴜsᴇʀ_ᴊᴏɪɴᴇᴅ\n"
                    f"机器人开发者刚刚加入了群组"
                )
                continue

            # Welcome Sudos
            elif new_mem.id in DRAGONS:
                update.effective_message.reply_text(
                    "哇！一条龙级灾难刚刚加入！保持警惕！",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#ᴜsᴇʀ_ᴊᴏɪɴᴇᴅ\n"
                    f"机器人超管刚刚加入了群组"
                )
                continue

            # Welcome Support
            elif new_mem.id in DEMONS:
                update.effective_message.reply_text(
                    "哼！一个鬼级灾难刚刚加入！",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"机器人支持成员刚刚加入了群组"
                )
                continue

            # Welcome Whitelisted
            elif new_mem.id in TIGERS:
                update.effective_message.reply_text(
                    "吼！一只虎级灾难刚刚加入！", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"一位白名单用户加入了群组"
                )
                continue

            # Welcome Tigers
            elif new_mem.id in WOLVES:
                update.effective_message.reply_text(
                    "嗷！一只狼级灾难刚刚加入！", reply_to_message_id=reply
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#USER_JOINED\n"
                    f"一位白名单用户加入了群组"
                )
                continue

            # Welcome yourself
            elif new_mem.id == bot.id:
                if not MukeshRobot.ALLOW_CHATS:
                    with suppress(BadRequest):
                        update.effective_message.reply_text(
                            f"群组功能对 {bot.first_name} 已禁用，我很忙。"
                        )
                    bot.leave_chat(update.effective_chat.id)
                    return
                bot.send_message(
                    EVENT_LOGS,
                    "#ɴᴇᴡ_ɢʀᴏᴜᴘ\n<b>群组名称：</b> {}\n<b>群组 ID：</b> <code>{}</code> ".format(
                        html.escape(chat.title),
                        chat.id,
                    ),
                    parse_mode=ParseMode.HTML,
                )
                update.effective_message.reply_text(
                    "我来了！", reply_to_message_id=reply
                )
                continue

            else:
                buttons = sql.get_welc_buttons(chat.id)
                keyb = build_keyboard(buttons)

                if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                    media_wel = True

                first_name = (
                    new_mem.first_name or "PersonWithNoName"
                )  # edge case of empty name - occurs for some bugs.

                if cust_welcome:
                    if cust_welcome == sql.DEFAULT_WELCOME:
                        cust_welcome = random.choice(
                            sql.DEFAULT_WELCOME_MESSAGES
                        ).format(first=escape_markdown(first_name))

                    if new_mem.last_name:
                        fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                    else:
                        fullname = escape_markdown(first_name)
                    count = chat.get_member_count()
                    mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                    if new_mem.username:
                        username = "@" + escape_markdown(new_mem.username)
                    else:
                        username = mention

                    valid_format = escape_invalid_curly_brackets(
                        cust_welcome, VALID_WELCOME_FORMATTERS
                    )
                    res = valid_format.format(
                        first=escape_markdown(first_name),
                        last=escape_markdown(new_mem.last_name or first_name),
                        fullname=escape_markdown(fullname),
                        username=username,
                        mention=mention,
                        count=count,
                        chatname=escape_markdown(chat.title),
                        id=new_mem.id,
                    )

                else:
                    res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                    keyb = []

                backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
                )
                keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None
            reply = None

        # User exceptions from welcomemutes
        if (
            is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id:
            if should_mute:
                if welc_mutes == "soft":
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_add_web_page_previews=False,
                        ),
                        until_date=(int(time.time() + 24 * 60 * 60)),
                    )
                if welc_mutes == "strong":
                    welcome_bool = False
                    if not media_wel:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "media_wel": False,
                                    "status": False,
                                    "update": update,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "backup_message": backup_message,
                                }
                            }
                        )
                    else:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "chat_id": chat.id,
                                    "status": False,
                                    "media_wel": True,
                                    "cust_content": cust_content,
                                    "welc_type": welc_type,
                                    "res": res,
                                    "keyboard": keyboard,
                                }
                            }
                        )
                    new_join_mem = f'<a href="tg://user?id={user.id}">{html.escape(new_mem.first_name)}</a>'
                    message = msg.reply_text(
                        f"{new_join_mem}，请点击下方按钮证明你是真人。\n 你有 120 秒时间。",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                {
                                    InlineKeyboardButton(
                                        text="是的，我是真人",
                                        callback_data=f"user_join_({new_mem.id})",
                                    )
                                }
                            ]
                        ),
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=reply,
                    )
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                        ),
                    )
                    job_queue.run_once(
                        partial(check_not_bot, new_mem, chat.id, message.message_id),
                        120,
                        name="welcomemute",
                    )

        if welcome_bool:
            if media_wel:
                sent = ENUM_FUNC_MAP[welc_type](
                    chat.id,
                    cust_content,
                    caption=res,
                    reply_markup=keyboard,
                    reply_to_message_id=reply,
                    parse_mode="markdown",
                )
            else:
                sent = send(update, res, keyboard, backup_message)
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if welcome_log:
            return welcome_log

        return (
            f"{html.escape(chat.title)}\n"
            f"#USER_JOINED\n"
            f"<b>用户</b>: {mention_html(user.id, user.first_name)}\n"
            f"<b>ID</b>: <code>{user.id}</code>"
        )

    return ""


def check_not_bot(member, chat_id, message_id, context):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop(member.id)
    member_status = member_dict.get("status")
    if not member_status:
        try:
            bot.unban_chat_member(chat_id, member.id)
        except:
            pass

        try:
            bot.edit_message_text(
                "*踢出用户*\n他们随时可以重新加入并再次尝试。",
                chat_id=chat_id,
                message_id=message_id,
            )
        except:
            pass


def left_member(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    if should_goodbye:
        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            try:
                dispatcher.bot.delete_message(chat.id, update.message.message_id)
            except BadRequest:
                pass
            reply = False

        left_mem = update.effective_message.left_chat_member
        if left_mem:

            # Dont say goodbyes to gbanned users
            if is_user_gbanned(left_mem.id):
                return

            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type != sql.Types.TEXT and goodbye_type != sql.Types.BUTTON_TEXT:
                ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = chat.get_member_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye, VALID_WELCOME_FORMATTERS
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(left_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=left_mem.id,
                )
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                    first=first_name
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

            send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@user_admin
def welcome(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        update.effective_message.reply_text(
            f"此群的欢迎消息设置为：`{pref}`。\n"
            f"*欢迎消息（未填充变量）为：*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type == sql.Types.BUTTON_TEXT or welcome_type == sql.Types.TEXT:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            update.effective_message.reply_text(
                "好的！有新成员加入时我会发送欢迎消息。"
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            update.effective_message.reply_text(
                "好，那我就不欢迎任何人了。"
            )

        else:
            update.effective_message.reply_text(
                "我只接受 'on/yes' 或 'off/no'！"
            )


@user_admin
def goodbye(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        update.effective_message.reply_text(
            f"此群的离开消息设置为：`{pref}`。\n"
            f"*离开消息（未填充变量）为：*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        else:
            if noformat:
                ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

            else:
                ENUM_FUNC_MAP[goodbye_type](
                    chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            update.effective_message.reply_text("好的！")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            update.effective_message.reply_text("好的！")

        else:
            # idek what you're writing, say yes or no
            update.effective_message.reply_text(
                "我只接受 'on/yes' 或 'off/no'！"
            )


@user_admin
@loggable
def set_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("你没有指定回复内容！")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    msg.reply_text("自定义欢迎消息设置成功！")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_WELCOME\n"
        f"<b>管理员：</b> {mention_html(user.id, user.first_name)}\n"
        f"设置了欢迎消息。"
    )


@user_admin
@loggable
def reset_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    update.effective_message.reply_text(
        "欢迎消息已重置为默认内容！"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_WELCOME\n"
        f"<b>管理员：</b> {mention_html(user.id, user.first_name)}\n"
        f"已将欢迎消息重置为默认内容。"
    )


@user_admin
@loggable
def set_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("你没有指定回复内容！")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    msg.reply_text("自定义离开消息设置成功！")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#SET_GOODBYE\n"
        f"<b>管理员：</b> {mention_html(user.id, user.first_name)}\n"
        f"设置了离开消息。"
    )


@user_admin
@loggable
def reset_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
    update.effective_message.reply_text(
        "离开消息已重置为默认内容！"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>管理员：</b> {mention_html(user.id, user.first_name)}\n"
        f"已将离开消息重置为默认内容。"
    )


@user_admin
@loggable
def welcomemute(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            msg.reply_text("成员加入时将不再被静音！")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• 管理员：</b> {mention_html(user.id, user.first_name)}\n"
                f"已将欢迎静音切换为 <b>OFF</b>。"
            )
        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            msg.reply_text(
                "新成员发送媒体的权限将被限制 24 小时。"
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• 管理员：</b> {mention_html(user.id, user.first_name)}\n"
                f"已将欢迎静音切换为 <b>SOFT</b>。"
            )
        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            msg.reply_text(
                "新成员加入后将被静音，直到他们证明自己不是机器人。\n他们有 120 秒时间，否则将被踢出。"
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>• 管理员：</b> {mention_html(user.id, user.first_name)}\n"
                f"已将欢迎静音切换为 <b>STRONG</b>。"
            )
        else:
            msg.reply_text(
                "请输入 <code>off</code>/<code>no</code>/<code>soft</code>/<code>strong</code> 之一！",
                parse_mode=ParseMode.HTML,
            )
            return ""
    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"\n 请给出一个设置！\n只能选择：<code>off</code>/<code>no</code> 或 <code>soft</code> 或 <code>strong</code>！\n"
            f"当前设置：<code>{curr_setting}</code>"
        )
        msg.reply_text(reply, parse_mode=ParseMode.HTML)
        return ""


@user_admin
@loggable
def clean_welcome(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            update.effective_message.reply_text(
                "我会删除两天内的旧欢迎消息。"
            )
        else:
            update.effective_message.reply_text(
                "我目前不会删除旧欢迎消息！"
            )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        update.effective_message.reply_text("我会尝试删除旧的欢迎消息！")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>管理员：</b> {mention_html(user.id, user.first_name)}\n"
            f"已将清理欢迎消息切换为 <code>ON</code>。"
        )
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        update.effective_message.reply_text("我不会删除旧的欢迎消息了。")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CLEAN_WELCOME\n"
            f"<b>管理员：</b> {mention_html(user.id, user.first_name)}\n"
            f"已将清理欢迎消息切换为 <code>OFF</code>。"
        )
    else:
        update.effective_message.reply_text("我只接受 'on/yes' 或 'off/no'！")
        return ""


@user_admin
def cleanservice(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat  # type: Optional[Chat]
    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var in ("no", "off"):
                sql.set_clean_service(chat.id, False)
                update.effective_message.reply_text("清理服务消息：已关闭")
            elif var in ("yes", "on"):
                sql.set_clean_service(chat.id, True)
                update.effective_message.reply_text("清理服务消息：已开启")
            else:
                update.effective_message.reply_text(
                    "无效选项", parse_mode=ParseMode.HTML
                )
        else:
            update.effective_message.reply_text(
                "用法：<code>on</code>/<code>yes</code> 或 <code>off</code>/<code>no</code>",
                parse_mode=ParseMode.HTML,
            )
    else:
        curr = sql.clean_service(chat.id)
        if curr:
            update.effective_message.reply_text(
                "清理服务消息：<code>on</code>", parse_mode=ParseMode.HTML
            )
        else:
            update.effective_message.reply_text(
                "清理服务消息：<code>off</code>", parse_mode=ParseMode.HTML
            )


def user_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST.pop(user.id)
        member_dict["status"] = True
        VERIFIED_USER_WAITLIST.update({user.id: member_dict})
        query.answer(text="验证成功！你是真人，已解除静音！")
        bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        try:
            bot.deleteMessage(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        query.answer(text="你无权执行此操作！")



WELC_HELP_TXT = (
    "群组的欢迎/离开消息可以通过多种方式个性化设置。如果你希望消息针对每个用户单独生成（就像默认欢迎消息那样），"
    "可以使用*以下*变量：\n"
    " • `{first}`*:* 代表用户的*名字*\n"
    " • `{last}`*:* 代表用户的*姓氏*。如果用户没有姓氏，则默认为*名字*。\n"
    " • `{fullname}`*:* 代表用户的*全名*。如果用户没有姓氏，则默认为*名字*。\n"
    " • `{username}`*:* 代表用户的*用户名*。如果没有用户名，则默认为*提及*用户名字。\n"
    " • `{mention}`*:* 简单地*提及*用户——用其名字标记。\n"
    " • `{id}`*:* 代表用户的 *ID*\n"
    " • `{count}`*:* 代表用户的*成员编号*。\n"
    " • `{chatname}`*:* 代表*当前群组名称*。\n"
    "\n每个变量必须用 `{}` 包裹才能被替换。\n"
    "欢迎消息同样支持 Markdown，可以让文字显示为粗体/斜体/代码/链接。"
    "也支持按钮，让你的欢迎消息配上精美的按钮更加出彩。\n"
    f"要创建一个链接到群规的按钮，请使用：`[规则](buttonurl://t.me/{dispatcher.bot.username}?start=group_id)`。"
    "只需将 `group_id` 替换为群组 ID（可通过 /id 获取）即可。"
    "注意群组 ID 通常以 `-` 开头，这是必须的，请勿删除。\n"
    "你还可以通过回复图片/GIF/视频/语音消息，然后发送 `/setwelcome` 将其设置为欢迎消息。"
)

WELC_MUTE_HELP_TXT = (
    "你可以让机器人对加入群组的新成员进行静音，从而防止垃圾机器人刷屏。"
    "以下是可用选项：\n"
    "• `/welcomemute  soft`*:* 限制新成员 24 小时内无法发送媒体。\n"
    "• `/welcomemute  strong`*:* 对新成员静音，直到他们点击按钮验证自己是真人。\n"
    "• `/welcomemute  off`*:* 关闭欢迎静音。\n"
    "*注意:* strong 模式下，若用户在 120 秒内未完成验证将被踢出。但他们随时可以重新加入。"
)


@user_admin
def welcome_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN)


@user_admin
def welcome_mute_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN
    )


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    goodbye_pref = sql.get_gdbye_pref(chat_id)[0]
    return (
        "此群的欢迎消息设置为 `{}`。\n"
        "离开消息设置为 `{}`。".format(welcome_pref, goodbye_pref)
    )


__help__ = """
 ❍ /welcome <开/关>*:* 开启或关闭欢迎消息。
 ❍ /welcome*:* 显示当前欢迎消息设置。
 ❍ /welcome noformat*:* 显示无格式的欢迎消息——便于回收利用。
 ❍ /goodbye*:* 类似 /welcome，但针对离开消息。
 ❍ /setwelcome <欢迎内容>*:* 设置自定义欢迎消息。支持 Markdown、按钮和媒体。
 ❍ /setgoodbye <再见内容>*:* 设置自定义再见消息。支持 Markdown、按钮和媒体。
 ❍ /resetwelcome*:* 恢复默认欢迎消息。
 ❍ /resetgoodbye*:* 恢复默认再见消息。
 ❍ /cleanwelcome <开/关>*:* 有新成员加入时，尝试删除上一条欢迎消息以避免刷屏。
 ❍ /welcomemutehelp*:* 显示欢迎静音的相关信息。
 ❍ /cleanservice <开/关>*:* 删除 Telegram 的加入/离开服务消息。
 ❍ /welcomehelp*:* 查看自定义欢迎/再见消息的更多格式说明。
"""

NEW_MEM_HANDLER = MessageHandler(
    Filters.status_update.new_chat_members, new_member, run_async=True
)
LEFT_MEM_HANDLER = MessageHandler(
    Filters.status_update.left_chat_member, left_member, run_async=True
)
WELC_PREF_HANDLER = CommandHandler(
    "welcome", welcome, filters=Filters.chat_type.groups, run_async=True
)
GOODBYE_PREF_HANDLER = CommandHandler(
    "goodbye", goodbye, filters=Filters.chat_type.groups, run_async=True
)
SET_WELCOME = CommandHandler(
    "setwelcome", set_welcome, filters=Filters.chat_type.groups, run_async=True
)
SET_GOODBYE = CommandHandler(
    "setgoodbye", set_goodbye, filters=Filters.chat_type.groups, run_async=True
)
RESET_WELCOME = CommandHandler(
    "resetwelcome", reset_welcome, filters=Filters.chat_type.groups, run_async=True
)
RESET_GOODBYE = CommandHandler(
    "resetgoodbye", reset_goodbye, filters=Filters.chat_type.groups, run_async=True
)
WELCOMEMUTE_HANDLER = CommandHandler(
    "welcomemute", welcomemute, filters=Filters.chat_type.groups, run_async=True
)
CLEAN_SERVICE_HANDLER = CommandHandler(
    "cleanservice", cleanservice, filters=Filters.chat_type.groups, run_async=True
)
CLEAN_WELCOME = CommandHandler(
    "cleanwelcome", clean_welcome, filters=Filters.chat_type.groups, run_async=True
)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help, run_async=True)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help, run_async=True)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_button, pattern=r"user_join_", run_async=True
)

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(LEFT_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(GOODBYE_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(SET_GOODBYE)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(RESET_GOODBYE)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOME_HELP)
dispatcher.add_handler(WELCOMEMUTE_HANDLER)
dispatcher.add_handler(CLEAN_SERVICE_HANDLER)
dispatcher.add_handler(BUTTON_VERIFY_HANDLER)
dispatcher.add_handler(WELCOME_MUTE_HELP)

__mod_name__ = "欢迎"
__command_list__ = []
__handlers__ = [
    NEW_MEM_HANDLER,
    LEFT_MEM_HANDLER,
    WELC_PREF_HANDLER,
    GOODBYE_PREF_HANDLER,
    SET_WELCOME,
    SET_GOODBYE,
    RESET_WELCOME,
    RESET_GOODBYE,
    CLEAN_WELCOME,
    WELCOME_HELP,
    WELCOMEMUTE_HANDLER,
    CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
