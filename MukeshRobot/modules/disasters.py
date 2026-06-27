import html
import json
import os
from typing import Optional

from telegram import ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

from MukeshRobot import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    OWNER_ID,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    dispatcher,
)
from MukeshRobot.modules.helper_funcs.chat_status import (
    dev_plus,
    sudo_plus,
    whitelist_plus,
)
from MukeshRobot.modules.helper_funcs.extraction import extract_user
from MukeshRobot.modules.log_channel import gloggable


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "这是一个群组，不是用户！"

    elif user_id == bot.id:
        reply = "这个操作无法对机器人自身执行。"

    else:
        reply = None
    return reply


@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in DRAGONS:
        message.reply_text("该用户已经是超级管理员（Dragon）了")
        return ""

    if user_id in DEMONS:
        rt += "已请求将支持用户（Demon）晋升为超级管理员（Dragon）。"

        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "已请求将白名单用户（Wolf）晋升为超级管理员（Dragon）。"

        WOLVES.remove(user_id)


    DRAGONS.append(user_id)


    update.effective_message.reply_text(
        rt
        + "\n已成功将 {} 设置为超级管理员（Dragon）！".format(
            user_member.first_name
        )
    )

    log_message = (
        f"#SUDO\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in DRAGONS:
        rt += "已请求将超级管理员（Dragon）降级为支持用户（Demon）"

        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("该用户已经是支持用户（Demon）了。")
        return ""

    if user_id in WOLVES:
        rt += "已请求将白名单用户（Wolf）晋升为支持用户（Demon）"

        WOLVES.remove(user_id)


    DEMONS.append(user_id)


    update.effective_message.reply_text(
        rt + f"\n{user_member.first_name} 已被添加为支持用户（Demon）！"
    )

    log_message = (
        f"#SUPPORT\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    

    if user_id in DRAGONS:
        rt += "该用户是超级管理员（Dragon），将降级为白名单用户（Wolf）。"

        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "该用户是支持用户（Demon），将降级为白名单用户（Wolf）。"

        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("该用户已经是白名单用户（Wolf）了。")
        return ""


    WOLVES.append(user_id)


    update.effective_message.reply_text(
        rt + f"\n已成功将 {user_member.first_name} 晋升为白名单用户（Wolf）！"
    )

    log_message = (
        f"#WHITELIST\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in DRAGONS:
        rt += "该用户是超级管理员（Dragon），将降级为 Tiger。"

        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "该用户是支持用户（Demon），将降级为 Tiger。"

        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "该用户是白名单用户（Wolf），将降级为 Tiger。"

        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("该用户已经是 Tiger 了。")
        return ""


    TIGERS.append(user_id)


    update.effective_message.reply_text(
        rt + f"\n已成功将 {user_member.first_name} 晋升为 Tiger！"
    )

    log_message = (
        f"#TIGER\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in DRAGONS:
        message.reply_text("已请求将该用户从超级管理员（Dragon）降级为普通用户")
        DRAGONS.remove(user_id)
        

        
        log_message = (
            f"#UNSUDO\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        message.reply_text("该用户不是超级管理员（Dragon）！")
        return ""


@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in DEMONS:
        message.reply_text("已请求将该用户从支持用户（Demon）降级为普通用户")
        DEMONS.remove(user_id)
        

        
        log_message = (
            f"#UNSUPPORT\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("该用户不是支持用户（Demon）！")
        return ""


@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in WOLVES:
        message.reply_text("已降级为普通用户")
        WOLVES.remove(user_id)
        

        
        log_message = (
            f"#UNWHITELIST\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("该用户不是白名单用户（Wolf）！")
        return ""


@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    
    if user_id in TIGERS:
        message.reply_text("已降级为普通用户")
        TIGERS.remove(user_id)
        

        
        log_message = (
            f"#UNTIGER\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("该用户不是 Tiger！")
        return ""


@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>已知白名单用户（Wolf）🐺：</b>\n"
    m = update.effective_message.reply_text(
        "<code>..</code>", parse_mode=ParseMode.HTML
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>已知 Tiger 用户 🐯：</b>\n"
    m = update.effective_message.reply_text(
        "<code>正在收集信息……</code>", parse_mode=ParseMode.HTML
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>正在收集信息……</code>", parse_mode=ParseMode.HTML
    )
    reply = "<b>已知支持用户（Demon）👹：</b>\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>正在收集信息……</code>", parse_mode=ParseMode.HTML
    )
    true_sudo = list(set(DRAGONS)- set(DEV_USERS))
    reply = "<b>已知超级管理员（Dragon）🐉：</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>正在收集信息……</code>", parse_mode=ParseMode.HTML
    )
    true_dev = list(set(DEV_USERS) -{OWNER_ID})
    reply = "✨ <b>开发者用户列表：</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


__help__ = f"""
*⚠️ 注意：*
以下命令仅对拥有特殊权限的用户有效，主要用于故障排查和调试目的。
群组管理员/群组所有者无需使用这些命令。

*列出所有特权用户：*
 ❍ /sudolist*：* 列出所有超级管理员（Dragon）
 ❍ /supportlist *：* 列出所有支持用户（Demon）
 ❍ /tigers *：* 列出所有 Tiger 用户
 ❍ /wolves *：* 列出所有白名单用户（Wolf）
 ❍ /devlist *：* 列出所有开发者
 ❍ /addsudo  *：* 将用户添加为超级管理员（Dragon）
 ❍ /adddemon *：* 将用户添加为支持用户（Demon）
 ❍ /addtiger *：* 将用户添加为 Tiger
 ❍ /addwolf*：* 将用户添加为白名单用户（Wolf）
 ❍ `添加开发者命令不存在，开发者应自行知道如何添加`

*Ping：*
 ❍ /ping *：* 获取机器人到 Telegram 服务器的延迟时间

*广播：（仅限机器人所有者）*
*注意：* 支持基本 Markdown 格式
 ❍ /broadcastall *：* 向所有地方广播
 ❍ broadcastusers *：* 向所有用户广播
 ❍ /broadcastgroups *：* 向所有群组广播



`⚠️ 请从顶部开始阅读`
访问[支持群]("https://t.me{SUPPORT_CHAT}")获取更多信息。
"""

SUDO_HANDLER = CommandHandler("addsudo", addsudo, run_async=True)
SUPPORT_HANDLER = CommandHandler(("addsupport", "adddemon"), addsupport, run_async=True)
TIGER_HANDLER = CommandHandler(("addtiger"), addtiger, run_async=True)
WHITELIST_HANDLER = CommandHandler(
    ("addwhitelist", "addwolf"), addwhitelist, run_async=True
)
UNSUDO_HANDLER = CommandHandler(("removesudo", "rmsudo"), removesudo, run_async=True)
UNSUPPORT_HANDLER = CommandHandler(
    ("removesupport", "removedemon"), removesupport, run_async=True
)
UNTIGER_HANDLER = CommandHandler(("removetiger"), removetiger, run_async=True)
UNWHITELIST_HANDLER = CommandHandler(
    ("removewhitelist", "removewolf"), removewhitelist, run_async=True
)
WHITELISTLIST_HANDLER = CommandHandler(
    ["whitelistlist", "wolves"], whitelistlist, run_async=True
)
TIGERLIST_HANDLER = CommandHandler(["tigers"], tigerlist, run_async=True)
SUPPORTLIST_HANDLER = CommandHandler("supportlist", supportlist, run_async=True)
SUDOLIST_HANDLER = CommandHandler("sudolist", sudolist, run_async=True)
DEVLIST_HANDLER = CommandHandler("devlist", devlist, run_async=True)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)
dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)

__mod_name__ = "超级管理"
__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
