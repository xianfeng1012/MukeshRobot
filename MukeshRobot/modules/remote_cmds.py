from telegram import ChatPermissions, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler

from MukeshRobot import dispatcher,LOGGER
from MukeshRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    is_bot_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from MukeshRobot.modules.helper_funcs.extraction import extract_user_and_text
from MukeshRobot.modules.helper_funcs.filters import CustomFilters

RBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to punch it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can punch group administrators",
    "Channel_private",
    "Not in the chat",
}

RUNBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to punch it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can punch group administrators",
    "Channel_private",
    "Not in the chat",
}

RKICK_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to punch it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can punch group administrators",
    "Channel_private",
    "Not in the chat",
}

RMUTE_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to punch it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can punch group administrators",
    "Channel_private",
    "Not in the chat",
}

RUNMUTE_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to punch it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can punch group administrators",
    "Channel_private",
    "Not in the chat",
}


@bot_admin
def rban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("未指定群组或用户。")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "未指定用户，或提供的 ID 不正确。"
        )
        return
    elif not chat_id:
        message.reply_text("未指定群组。")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "找不到该群组！请确认群组 ID 正确且我已加入该群组。"
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("抱歉，这是一个私聊！")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "我无法在那里限制成员！请确认我是管理员且拥有封禁用户的权限。"
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("找不到该用户。")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("我真希望能封禁管理员……但做不到。")
        return

    if user_id == bot.id:
        message.reply_text("我不会封禁我自己，你在开玩笑吗？")
        return

    try:
        chat.ban_member(user_id)
        message.reply_text("已从该群组封禁！")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("已封禁！", quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("操作失败，无法封禁该用户。")


@bot_admin
def runban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("未指定群组或用户。")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "未指定用户，或提供的 ID 不正确。"
        )
        return
    elif not chat_id:
        message.reply_text("未指定群组。")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "找不到该群组！请确认群组 ID 正确且我已加入该群组。"
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("抱歉，这是一个私聊！")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "我无法在那里解除限制！请确认我是管理员且拥有解除封禁的权限。"
        )
        return

    try:
        chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("在该群组中找不到该用户。")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "该用户已在群组中，为什么还要远程解除封禁？"
        )
        return

    if user_id == bot.id:
        message.reply_text("我不会解除自己的封禁，我本来就是那里的管理员！")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("好的，该用户现在可以加入该群组了！")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("已解除封禁！", quote=False)
        elif excp.message in RUNBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR unbanning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("操作失败，无法解除该用户的封禁。")


@bot_admin
def rkick(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("未指定群组或用户。")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "未指定用户，或提供的 ID 不正确。"
        )
        return
    elif not chat_id:
        message.reply_text("未指定群组。")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "找不到该群组！请确认群组 ID 正确且我已加入该群组。"
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("抱歉，这是一个私聊！")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "我无法在那里限制成员！请确认我是管理员且拥有踢出用户的权限。"
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("找不到该用户。")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("我真希望能踢出管理员……但做不到。")
        return

    if user_id == bot.id:
        message.reply_text("我不会踢出我自己，你在开玩笑吗？")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("已从群组踢出！")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("已踢出！", quote=False)
        elif excp.message in RKICK_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR punching user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("操作失败，无法踢出该用户。")


@bot_admin
def rmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("未指定群组或用户。")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "未指定用户，或提供的 ID 不正确。"
        )
        return
    elif not chat_id:
        message.reply_text("未指定群组。")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "找不到该群组！请确认群组 ID 正确且我已加入该群组。"
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("抱歉，这是一个私聊！")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "我无法在那里限制成员！请确认我是管理员且拥有禁言用户的权限。"
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("找不到该用户。")
            return
        else:
            raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("我真希望能禁言管理员……但做不到。")
        return

    if user_id == bot.id:
        message.reply_text("我不会禁言我自己，你在开玩笑吗？")
        return

    try:
        bot.restrict_chat_member(
            chat.id, user_id, permissions=ChatPermissions(can_send_messages=False)
        )
        message.reply_text("已在该群组禁言！")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("已禁言！", quote=False)
        elif excp.message in RMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR mute user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("操作失败，无法禁言该用户。")


@bot_admin
def runmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("未指定群组或用户。")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "未指定用户，或提供的 ID 不正确。"
        )
        return
    elif not chat_id:
        message.reply_text("未指定群组。")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "找不到该群组！请确认群组 ID 正确且我已加入该群组。"
            )
            return
        else:
            raise

    if chat.type == "private":
        message.reply_text("抱歉，这是一个私聊！")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "我无法在那里解除限制！请确认我是管理员且拥有解除封禁的权限。"
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("在该群组中找不到该用户。")
            return
        else:
            raise

    if is_user_in_chat(chat, user_id):
        if (
            member.can_send_messages
            and member.can_send_media_messages
            and member.can_send_other_messages
            and member.can_add_web_page_previews
        ):
            message.reply_text("该用户在该群组中已有发言权限。")
            return

    if user_id == bot.id:
        message.reply_text("我不会解除自己的禁言，我本来就是那里的管理员！")
        return

    try:
        bot.restrict_chat_member(
            chat.id,
            int(user_id),
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        message.reply_text("好的，该用户现在可以在该群组中发言了！")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("已解除禁言！", quote=False)
        elif excp.message in RUNMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR unmnuting user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("操作失败，无法解除该用户的禁言。")


RBAN_HANDLER = CommandHandler(
    "rban", rban, filters=CustomFilters.sudo_filter, run_async=True
)
RUNBAN_HANDLER = CommandHandler(
    "runban", runban, filters=CustomFilters.sudo_filter, run_async=True
)
RKICK_HANDLER = CommandHandler(
    "rpunch", rkick, filters=CustomFilters.sudo_filter, run_async=True
)
RMUTE_HANDLER = CommandHandler(
    "rmute", rmute, filters=CustomFilters.sudo_filter, run_async=True
)
RUNMUTE_HANDLER = CommandHandler(
    "runmute", runmute, filters=CustomFilters.sudo_filter, run_async=True
)

dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
dispatcher.add_handler(RKICK_HANDLER)
dispatcher.add_handler(RMUTE_HANDLER)
dispatcher.add_handler(RUNMUTE_HANDLER)
