import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from MukeshRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
)
from MukeshRobot.modules.helper_funcs.extraction import extract_user_and_text
from MukeshRobot.modules.helper_funcs.string_handling import extract_time
from MukeshRobot.modules.log_channel import gloggable, loggable


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("我怀疑那不是个用户。")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("好像找不到这个人。")
        return log_message
    if user_id == bot.id:
        message.reply_text("哦对，封禁我自己，菜鸟！")
        return log_message

    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("想让我对付神级灾害？")
        elif user_id in DEV_USERS:
            message.reply_text("我不能对自己人动手。")
        elif user_id in DRAGONS:
            message.reply_text(
                "在这里与这条龙战斗会危及平民生命。"
            )
        elif user_id in DEMONS:
            message.reply_text(
                "请先拿到英雄协会的命令再来对付恶魔级灾害。"
            )
        elif user_id in TIGERS:
            message.reply_text(
                "请先拿到英雄协会的命令再来对付虎级灾害。"
            )
        elif user_id in WOLVES:
            message.reply_text("狼级能力使他们免疫封禁！")
        else:
            message.reply_text("狼级能力使他们免疫封禁！")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'静默' if silent else ''}已封禁\n"
        f"<b>封禁者:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>用户:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += "\n<b>原因:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>封禁事件</b>\n"
            f"<code> </code><b>•  封禁者:</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>•  用户:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            reply += f"\n<code> </code><b>•  原因:</b> \n{html.escape(reason)}"
        bot.sendMessage(chat.id, reply, parse_mode=ParseMode.HTML)
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            message.reply_text("已封禁！", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("呃……好像没成功……")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("我怀疑那不是个用户。")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("好像找不到这个用户。")
        return log_message
    if user_id == bot.id:
        message.reply_text("我才不会封禁自己，你疯了吗？")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("我不想这么做。")
        return log_message

    if not reason:
        message.reply_text("你还没有指定封禁这个用户多长时间！")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "临时封禁\n"
        f"<b>封禁者:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>用户:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>时长:</b> {time_val}"
    )
    if reason:
        log += "\n<b>原因:</b> {}".format(reason)

    try:
        chat.ban_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"已封禁！用户 {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"现已被封禁 {time_val}。",
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                f"已封禁！该用户将被封禁 {time_val}。", quote=False
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("妈呀，我封禁不了这个用户。")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("我怀疑那不是个用户。")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("好像找不到这个用户。")
        return log_message
    if user_id == bot.id:
        message.reply_text("是的我才不要那样做。")
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text("我真希望能踢掉这个用户……")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"踢出一人！{mention_html(member.user.id, html.escape(member.user.first_name))}。",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"已踢出\n"
            f"<b>踢出者:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>用户:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>原因:</b> {reason}"

        return log

    else:
        message.reply_text("妈呀，我踢不了这个用户。")

    return log_message


@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("我希望可以……但你是管理员。")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*把你踢出了群组*")
    else:
        update.effective_message.reply_text("啊？我做不到:/")


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("我怀疑那不是个用户。")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("好像找不到这个用户。")
        return log_message
    if user_id == bot.id:
        message.reply_text("如果我不在这里，我怎么解封自己……？")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("这个人不是已经在群里了吗？")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("好的，这个用户可以加入了！")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"已解封\n"
        f"<b>解封者:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>用户:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>原因:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("请提供有效的聊天 ID。")
        return

    chat = bot.get_chat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("好像找不到这个用户。")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("你不是已经在这个聊天里了吗？")
        return

    chat.unban_member(user.id)
    message.reply_text("好的，我已经解封你了。")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"已解封\n"
        f"<b>解封者:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>用户:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


__help__ = """
 ❍ /kickme *:* 踢出发出该命令的用户

*仅管理员:*
 ❍ /ban <用户名>*:* 封禁一个用户。（通过用户名或回复）
 ❍ /sban  <用户名>*:* 静默封禁一个用户。删除命令、被回复的消息，且不回复。（通过用户名或回复）
 ❍ /tban  <用户名> x(m/h/d)*:* 封禁用户 `x` 时长。（通过用户名或回复）。`m` = `分钟`，`h` = `小时`，`d` = `天`。
 ❍ /unban  <用户名>*:* 解封一个用户。（通过用户名或回复）
 ❍ /kick <用户名>*:* 将用户踢出群组。（通过用户名或回复）
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban, run_async=True)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban, run_async=True)
KICK_HANDLER = CommandHandler("kick", kick, run_async=True)
UNBAN_HANDLER = CommandHandler("unban", unban, run_async=True)
ROAR_HANDLER = CommandHandler("roar", selfunban, run_async=True)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)

__mod_name__ = "封禁"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
]
