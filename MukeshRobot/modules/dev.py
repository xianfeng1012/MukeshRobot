import os
import subprocess
import sys
from contextlib import suppress
from time import sleep

from telegram import TelegramError, Update
from telegram.error import Unauthorized
from telegram.ext import CallbackContext, CommandHandler

import MukeshRobot
from MukeshRobot import dispatcher
from MukeshRobot.modules.helper_funcs.chat_status import dev_plus


@dev_plus
def allow_groups(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.effective_message.reply_text(f"当前状态：{MukeshRobot.ALLOW_CHATS}")
        return
    if args[0].lower() in ["off", "no"]:
        MukeshRobot.ALLOW_CHATS = True
    elif args[0].lower() in ["yes", "on"]:
        MukeshRobot.ALLOW_CHATS = False
    else:
        update.effective_message.reply_text("格式：/lockdown Yes/No 或 Off/On")
        return
    update.effective_message.reply_text("完成！锁定状态已切换。")


@dev_plus
def leave(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    if args:
        chat_id = str(args[0])
        try:
            bot.leave_chat(int(chat_id))
        except TelegramError:
            update.effective_message.reply_text(
                "哔哔，我无法退出该群组（原因未知）。"
            )
            return
        with suppress(Unauthorized):
            update.effective_message.reply_text("哔哔，已退出该群组！")
    else:
        update.effective_message.reply_text("请提供有效的群组 ID")


@dev_plus
def gitpull(update: Update, context: CallbackContext):
    sent_msg = update.effective_message.reply_text(
        "正在从远程拉取所有变更，随后尝试重启。"
    )
    subprocess.Popen("git pull", stdout=subprocess.PIPE, shell=True)

    sent_msg_text = sent_msg.text + "\n\n变更已拉取……重启倒计时："

    for i in reversed(range(5)):
        sent_msg.edit_text(sent_msg_text + str(i + 1))
        sleep(1)

    sent_msg.edit_text("已重启。")

    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


@dev_plus
def restart(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "正在启动新实例并关闭当前实例……"
    )

    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


LEAVE_HANDLER = CommandHandler("leave", leave, run_async=True)
GITPULL_HANDLER = CommandHandler("gitpull", gitpull, run_async=True)
RESTART_HANDLER = CommandHandler("reboot", restart, run_async=True)
ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups, run_async=True)

dispatcher.add_handler(ALLOWGROUPS_HANDLER)
dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(GITPULL_HANDLER)
dispatcher.add_handler(RESTART_HANDLER)



__handlers__ = [LEAVE_HANDLER, GITPULL_HANDLER, RESTART_HANDLER, ALLOWGROUPS_HANDLER]
