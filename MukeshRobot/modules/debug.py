import datetime
import os

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from telethon import events

from MukeshRobot import dispatcher, telethn
from MukeshRobot.modules.helper_funcs.chat_status import dev_plus

DEBUG_MODE = False


@dev_plus
def debug(update: Update, context: CallbackContext):
    global DEBUG_MODE
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    print(DEBUG_MODE)
    if len(args) > 1:
        if args[1] in ("yes", "on"):
            DEBUG_MODE = True
            message.reply_text("调试模式已开启。")
        elif args[1] in ("no", "off"):
            DEBUG_MODE = False
            message.reply_text("调试模式已关闭。")
    else:
        if DEBUG_MODE:
            message.reply_text("调试模式当前处于开启状态。")
        else:
            message.reply_text("调试模式当前处于关闭状态。")


@telethn.on(events.NewMessage(pattern="[/!].*"))
async def i_do_nothing_yes(event):
    global DEBUG_MODE
    if DEBUG_MODE:
        print(f"-{event.from_id} ({event.chat_id}) : {event.text}")
        if os.path.exists("updates.txt"):
            with open("updates.txt", "r") as f:
                text = f.read()
            with open("updates.txt", "w+") as f:
                f.write(text + f"\n-{event.from_id} ({event.chat_id}) : {event.text}")
        else:
            with open("updates.txt", "w+") as f:
                f.write(
                    f"- {event.from_id} ({event.chat_id}) : {event.text} | {datetime.datetime.now()}"
                )


support_chat = os.getenv("SUPPORT_CHAT")


@dev_plus
def logs(update: Update, context: CallbackContext):
    user = update.effective_user
    with open("log.txt", "rb") as f:
        context.bot.send_document(document=f, filename=f.name, chat_id=user.id)


LOG_HANDLER = CommandHandler("logs", logs, run_async=True)
dispatcher.add_handler(LOG_HANDLER)

DEBUG_HANDLER = CommandHandler("debug", debug, run_async=True)
dispatcher.add_handler(DEBUG_HANDLER)

__mod_name__ = "调试"
__help__ = """
/logs    获取机器人日志文件
/debug 开启 / 关闭调试模式"""
__command_list__ = ["debug"]
__handlers__ = [DEBUG_HANDLER]
