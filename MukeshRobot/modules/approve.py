import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.utils.helpers import mention_html

import MukeshRobot.modules.sql.approve_sql as sql
from MukeshRobot import DRAGONS, dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.chat_status import user_admin
from MukeshRobot.modules.helper_funcs.extraction import extract_user
from MukeshRobot.modules.log_channel import loggable


@loggable
@user_admin
def approve(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "我不知道你在说谁，请指定一个用户！"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text(
            "该用户已经是管理员——锁定、黑名单和防刷屏对其本就不适用。"
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) 已在 {chat_title} 中被批准",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ""
    sql.approve(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) 已在 {chat_title} 中获得批准！他们将不再受锁定、黑名单和防刷屏等自动管理操作的影响。",
        parse_mode=ParseMode.MARKDOWN,
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#APPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@loggable
@user_admin
def disapprove(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "我不知道你在说谁，请指定一个用户！"
        )
        return ""
    try:
        member = chat.get_member(user_id)
    except BadRequest:
        return ""
    if member.status == "administrator" or member.status == "creator":
        message.reply_text("此用户是管理员，无法取消批准。")
        return ""
    if not sql.is_approved(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} 尚未被批准！")
        return ""
    sql.disapprove(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} 已在 {chat_title} 中取消批准。"
    )
    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNAPPROVED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log_message


@user_admin
def approved(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "以下用户已被批准。\n"
    approved_users = sql.list_approved(message.chat_id)
    for i in approved_users:
        member = chat.get_member(int(i.user_id))
        msg += f"- `{i.user_id}`: {member.user['first_name']}\n"
    if msg.endswith("以下用户已被批准。\n"):
        message.reply_text(f"{chat_title} 中暂无已批准用户。")
        return ""
    else:
        message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


@user_admin
def approval(update, context):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    user_id = extract_user(message, args)
    member = chat.get_member(int(user_id))
    if not user_id:
        message.reply_text(
            "我不知道你在说谁，请指定一个用户！"
        )
        return ""
    if sql.is_approved(message.chat_id, user_id):
        message.reply_text(
            f"{member.user['first_name']} 是已批准用户，锁定、防刷屏和黑名单对其不适用。"
        )
    else:
        message.reply_text(
            f"{member.user['first_name']} 未被批准，将受到正常管理命令的约束。"
        )


def unapproveall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "只有群主才能一次性取消所有用户的批准。"
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="取消所有用户的批准", callback_data="unapproveall_user"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="取消", callback_data="unapproveall_cancel"
                    )
                ],
            ]
        )
        update.effective_message.reply_text(
            f"确定要取消 {chat.title} 中所有用户的批准吗？此操作无法撤销。",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def unapproveall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "unapproveall_user":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            approved_users = sql.list_approved(chat.id)
            users = [int(i.user_id) for i in approved_users]
            for user_id in users:
                sql.disapprove(chat.id, user_id)

        if member.status == "administrator":
            query.answer("只有群主才能执行此操作。")

        if member.status == "member":
            query.answer("你需要是管理员才能执行此操作。")
    elif query.data == "unapproveall_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("已取消移除所有已批准用户的操作。")
            return ""
        if member.status == "administrator":
            query.answer("只有群主才能执行此操作。")
        if member.status == "member":
            query.answer("你需要是管理员才能执行此操作。")


__help__ = """
有时，你可能信任某个用户不会发送不当内容。
也许还不足以让他们成为管理员，但你可以接受锁定、黑名单和防刷屏对其不适用。

这就是"批准"功能的用途——批准可信任的用户，让他们不受这些限制的约束。

*管理员命令：*
❍ /approval*：* 查看某用户在本群的批准状态。
❍ /approve *：* 批准某用户，锁定、黑名单和防刷屏将不再对其适用。
❍ /unapprove *：* 取消批准某用户，他们将重新受到锁定、黑名单和防刷屏的约束。
❍ /approved *：* 列出所有已批准的用户。
❍ /unapproveall *：* 取消批准群内*所有*用户，此操作无法撤销。
"""

APPROVE = DisableAbleCommandHandler("approve", approve, run_async=True)
DISAPPROVE = DisableAbleCommandHandler("unapprove", disapprove, run_async=True)
APPROVED = DisableAbleCommandHandler("approved", approved, run_async=True)
APPROVAL = DisableAbleCommandHandler("approval", approval, run_async=True)
UNAPPROVEALL = DisableAbleCommandHandler("unapproveall", unapproveall, run_async=True)
UNAPPROVEALL_BTN = CallbackQueryHandler(
    unapproveall_btn, pattern=r"unapproveall_.*", run_async=True
)

dispatcher.add_handler(APPROVE)
dispatcher.add_handler(DISAPPROVE)
dispatcher.add_handler(APPROVED)
dispatcher.add_handler(APPROVAL)
dispatcher.add_handler(UNAPPROVEALL)
dispatcher.add_handler(UNAPPROVEALL_BTN)

__mod_name__ = "批准"
__command_list__ = ["approve", "unapprove", "approved", "approval"]
__handlers__ = [APPROVE, DISAPPROVE, APPROVED, APPROVAL]
