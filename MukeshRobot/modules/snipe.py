from telegram import TelegramError, Update
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import CallbackContext, run_async

from MukeshRobot import LOGGER, dispatcher
from MukeshRobot.modules.helper_funcs.filters import CustomFilters


@run_async
def snipe(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError:
        update.effective_message.reply_text("请提供一个目标群组 ID！")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text(
                "无法发送消息，可能我不在该群组中。"
            )


__help__ = """
*仅限开发者：*
• /snipe <群组ID> <消息内容>
让机器人向指定群组发送一条消息。
"""

__mod_name__ = "狙击"

SNIPE_HANDLER = CommandHandler(
    "snipe", snipe, pass_args=True, filters=CustomFilters.dev_filter
)

dispatcher.add_handler(SNIPE_HANDLER)
