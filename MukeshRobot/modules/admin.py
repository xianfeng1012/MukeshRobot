import html
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

from MukeshRobot import DRAGONS, dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.admin_rights import user_can_changeinfo
from MukeshRobot.modules.helper_funcs.alternate import send_message
from MukeshRobot.modules.helper_funcs.chat_status import (
    ADMIN_CACHE,
    bot_admin,
    can_pin,
    connection_status,
    user_admin,
can_promote
)
#from MukeshRobot.utils.admins import can_promote
from MukeshRobot.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from MukeshRobot.modules.log_channel import loggable


@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text(
            "» 你没有权限更改群组信息！"
        )

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "» 请回复一个贴纸以将其设置为群组贴纸包！"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(f"» 已成功设置 {chat.title} 的群组贴纸！")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "» 你的群组需要至少 100 名成员才能设置群组贴纸包！"
                )
            msg.reply_text(f"错误！{excp.message}。")
    else:
        msg.reply_text("» 请回复一个贴纸以将其设置为群组贴纸包！")


@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("» 你没有权限更改群组信息！")
        return

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("» 你只能将图片设置为群组头像！")
            return
        dlmsg = msg.reply_text("» 正在更换群组头像……")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("» 已成功设置群组头像！")
        except BadRequest as excp:
            msg.reply_text(f"错误！{excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("» 请回复一张图片或文件以将其设置为群组头像！")


@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("» 你没有权限更改群组信息！")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("» 已成功删除群组头像！")
    except BadRequest as excp:
        msg.reply_text(f"错误！{excp.message}。")
        return


@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text(
            "» 你没有权限更改群组信息！"
        )

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("» 什么？你想设置一个空简介！")
    try:
        if len(desc) > 255:
            return msg.reply_text(
                "» 简介不能超过 255 个字符！"
            )
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(f"» 已成功更新 {chat.title} 的聊天简介！")
    except BadRequest as excp:
        msg.reply_text(f"错误！{excp.message}。")


@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("» 你没有权限更改群组信息！")
        return

    title = " ".join(args)
    if not title:
        msg.reply_text("» 请输入新的聊天标题！")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"» 已成功将 <b>{title}</b> 设置为新的聊天标题！",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"错误！{excp.message}。")
        return


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("» 你没有权限添加新管理员！")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "» 我不知道那个用户是谁，在我所在的群里从没见过他！",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» 在我看来那个用户已经是管理员了！")
        return

    if user_id == bot.id:
        message.reply_text(
            "» 我不能晋升自己，我的主人没叫我这么做。"
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("» 我看这个用户不在这里。")
        else:
            message.reply_text(
                "» 出了点问题，也许有人在我之前已经晋升了那个用户。"
            )
        return

    bot.sendMessage(
        chat.id,
        f"<b>» 在 {chat.title} 晋升用户</b>\n\n<b>被晋升:</b> {mention_html(user_member.user.id, user_member.user.first_name)}\n<b>操作者:</b> {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#已晋升\n"
        f"<b>操作者:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>用户:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def lowpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("» 你没有权限添加新管理员！")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "» 我不知道那个用户是谁，在我所在的群里从没见过他！",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» 在我看来那个用户已经是管理员了！")
        return

    if user_id == bot.id:
        message.reply_text(
            "» 我不能晋升自己，我的主人没叫我这么做。"
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_pin_messages=bot_member.can_pin_messages,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("» 我看这个用户不在这里。")
        else:
            message.reply_text(
                "» 出了点问题，也许有人在我之前已经晋升了那个用户。"
            )
        return

    bot.sendMessage(
        chat.id,
        f"<b>» 在 {chat.title} 低权限晋升用户</b>\n\n<b>被晋升:</b> {mention_html(user_member.user.id, user_member.user.first_name)}\n<b>操作者:</b> {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#低权限晋升\n"
        f"<b>操作者:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>用户:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def fullpromote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("» 你没有权限添加新管理员！")
        return

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "» 我不知道那个用户是谁，在我所在的群里从没见过他！",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("» 在我看来那个用户已经是管理员了！")
        return

    if user_id == bot.id:
        message.reply_text(
            "» 我不能晋升自己，我的主人没叫我这么做。"
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("» 我看这个用户不在这里。")
        else:
            message.reply_text(
                "» 出了点问题，也许有人在我之前已经晋升了那个用户。"
            )
        return

    bot.sendMessage(
        chat.id,
        f"» 在 <b>{chat.title}</b> 完全晋升用户\n\n<b>被晋升: {mention_html(user_member.user.id, user_member.user.first_name)}</b>\n<b>操作者: {mention_html(user.id, user.first_name)}</b>",
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#完全晋升\n"
        f"<b>操作者:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>用户:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@bot_admin
@can_promote
@user_admin
@loggable
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "» 我不知道那个用户是谁，在我所在的群里从没见过他！",
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status == "creator":
        message.reply_text(
            "» 那个用户是群主，我不想让自己陷入危险。"
        )
        return

    if not user_member.status == "administrator":
        message.reply_text("» 在我看来那个用户在这里不是管理员！")
        return

    if user_id == bot.id:
        message.reply_text("» 我不能降级自己，但如果你想，我可以退群。")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(
            chat.id,
            f"» 已成功降级 <b>{chat.title}</b> 中的管理员\n\n被降级: <b>{mention_html(user_member.user.id, user_member.user.first_name)}</b>\n操作者: {mention_html(user.id, user.first_name)}",
            parse_mode=ParseMode.HTML,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#已降级\n"
            f"<b>操作者:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>被降级:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        message.reply_text(
            "» 降级失败，也许我不是管理员，或者是别人晋升了那个用户！",
        )
        return


@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("» 已成功刷新管理员缓存！")


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "» 我不知道那个用户是谁，在我所在的群里从没见过他！",
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "» 那个用户是群主，我不想让自己陷入危险。",
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "» 我只能给管理员设置头衔！",
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "» 我不能给自己设置头衔，我的主人没叫我这么做。",
        )
        return

    if not title:
        message.reply_text(
            "» 你觉得设置空头衔会有什么用吗？"
        )
        return

    if len(title) > 16:
        message.reply_text(
            "» 头衔超过 16 个字符，将自动截断。",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "» 可能那个用户不是由我晋升的，或者你发送了不能用作头衔的内容。"
        )
        return

    bot.sendMessage(
        chat.id,
        f"» 已成功将 <code>{user_member.user.first_name or user_id}</code> "
        f"的头衔设置为 <code>{html.escape(title[:16])}</code>！",
        parse_mode=ParseMode.HTML,
    )


@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text("» 请回复一条消息以置顶！")
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(
                f"» 已成功置顶该消息。\n点击下方按钮查看消息。",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("查看消息", url=f"{message_link}")]]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#已置顶消息\n"
            f"<b>置顶者:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text(
            "» 你没有权限在此聊天中置顶/取消置顶消息！"
        )
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id, prev_message.message_id)
            msg.reply_text(
                f"» 已成功取消置顶 <a href='{message_link}'> 该消息</a>。",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text("» 已成功取消最后一条置顶消息。")
        except BadRequest as excp:
            if excp.message == "Message to unpin not found":
                msg.reply_text(
                    "» 我无法取消那条消息的置顶，也许消息太旧了，或者已被他人取消置顶。"
                )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#已取消置顶消息\n"
        f"<b>操作者:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(
            f"置顶于 {html.escape(chat.title)}。",
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="查看消息",
                            url=f"https://t.me/{link_chat_id}/{pinned_id}",
                        )
                    ]
                ]
            ),
        )

    else:
        msg.reply_text(
            f"» <b>{html.escape(chat.title)}</b> 中没有置顶消息！",
            parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "» 我没有权限访问邀请链接！",
            )
    else:
        update.effective_message.reply_text(
            "» 我只能提供群组和频道的邀请链接！",
        )


@connection_status
def adminlist(update, context):
    chat = update.effective_chat  # type: Optional[Chat] -> unused variable
    user = update.effective_user  # type: Optional[User]
    args = context.args  # -> unused variable
    bot = context.bot

    if update.effective_message.chat.type == "private":
        send_message(
            update.effective_message,
            "» 此命令只能在群组中使用，不能在私聊中使用。",
        )
        return

    update.effective_chat
    chat_id = update.effective_chat.id
    chat_name = update.effective_message.chat.title  # -> unused variable

    try:
        msg = update.effective_message.reply_text(
            "» 正在获取管理员列表……",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = update.effective_message.reply_text(
            "» 正在获取管理员列表……",
            quote=False,
            parse_mode=ParseMode.HTML,
        )

    administrators = bot.getChatAdministrators(chat_id)
    text = "<b>{}</b> 的管理员列表:".format(html.escape(update.effective_chat.title))

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ 已注销账号"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )

        if user.is_bot:
            administrators.remove(admin)
            continue

        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "creator":
            text += "\n 🥀 群主:"
            text += "\n<code> • </code>{}\n".format(name)

            if custom_title:
                text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

    text += "\n💫 管理员:"

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == "":
            name = "☠ 已注销账号"
        else:
            name = "{}".format(
                mention_html(
                    user.id,
                    html.escape(user.first_name + " " + (user.last_name or "")),
                ),
            )
        # if user.username:
        #    name = escape_markdown("@" + user.username)
        if status == "administrator":
            if custom_title:
                try:
                    custom_admin_list[custom_title].append(name)
                except KeyError:
                    custom_admin_list.update({custom_title: [name]})
            else:
                normal_admin_list.append(name)

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🔮 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    try:
        msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


__help__ = """
*用户命令*:
» /admins*:* 查看群内管理员列表
» /pinned*:* 获取当前置顶消息

*以下命令仅限管理员:*
» /pin*:* 静默置顶所回复的消息 - 加上 `'loud'` 或 `'notify'` 可通知用户
» /unpin*:* 取消当前置顶消息
» /invitelink*:* 获取邀请链接
» /promote*:* 晋升所回复的用户
» /lowpromote*:* 以半权限晋升所回复的用户
» /fullpromote*:* 以全权限晋升所回复的用户
» /demote*:* 降级所回复的用户
» /title <头衔>*:* 为机器人晋升的管理员设置自定义头衔
» /admincache*:* 强制刷新管理员列表
» /del*:* 删除所回复的消息
» /purge*:* 删除本消息到所回复消息之间的所有消息
» /purge <整数 X>*:* 如回复某条消息，则删除该消息及其后 X 条消息
» /setgtitle <文本>*:* 设置群组标题
» /setgpic*:* 回复一张图片以设置为群组头像
» /setdesc*:* 设置群组简介
» /setsticker*:* 设置群组贴纸
"""

SET_DESC_HANDLER = CommandHandler("setdesc", set_desc, run_async=True)
SET_STICKER_HANDLER = CommandHandler("setsticker", set_sticker, run_async=True)
SETCHATPIC_HANDLER = CommandHandler("setgpic", setchatpic, run_async=True)
RMCHATPIC_HANDLER = CommandHandler("delgpic", rmchatpic, run_async=True)
SETCHAT_TITLE_HANDLER = CommandHandler("setgtitle", setchat_title, run_async=True)

ADMINLIST_HANDLER = DisableAbleCommandHandler(
    ["admins", "staff"], adminlist, run_async=True
)

PIN_HANDLER = CommandHandler("pin", pin, run_async=True)
UNPIN_HANDLER = CommandHandler("unpin", unpin, run_async=True)
PINNED_HANDLER = CommandHandler("pinned", pinned, run_async=True)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, run_async=True)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler(
    "fullpromote", fullpromote, run_async=True
)
LOW_PROMOTE_HANDLER = DisableAbleCommandHandler(
    "lowpromote", lowpromote, run_async=True
)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
ADMIN_REFRESH_HANDLER = CommandHandler(
    ["admincache", "reload", "refresh"],
    refresh_admin,
    run_async=True,
)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(ADMINLIST_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(LOW_PROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "管理员"
__command_list__ = [
    "setdesc" "setsticker" "setgpic" "delgpic" "setgtitle" "adminlist",
    "admins",
    "invitelink",
    "promote",
    "fullpromote",
    "lowpromote",
    "demote",
    "admincache",
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    FULLPROMOTE_HANDLER,
    LOW_PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
