import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from MukeshRobot import CASH_API_KEY, dispatcher


def convert(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(" ")

    if len(args) == 4:
        try:
            orig_cur_amount = float(args[1])

        except ValueError:
            update.effective_message.reply_text("无效的货币金额")
            return

        orig_cur = args[2].upper()

        new_cur = args[3].upper()

        request_url = (
            f"https://www.alphavantage.co/query"
            f"?function=CURRENCY_EXCHANGE_RATE"
            f"&from_currency={orig_cur}"
            f"&to_currency={new_cur}"
            f"&apikey={CASH_API_KEY}"
        )
        response = requests.get(request_url).json()
        try:
            current_rate = float(
                response["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
            )
        except KeyError:
            update.effective_message.reply_text("无效的货币代码，暂不支持该货币。")
            return
        new_cur_amount = round(orig_cur_amount * current_rate, 5)
        update.effective_message.reply_text(
            f"{orig_cur_amount} {orig_cur} = {new_cur_amount} {new_cur}"
        )

    elif len(args) == 1:
        update.effective_message.reply_text(__help__, parse_mode=ParseMode.MARKDOWN)

    else:
        update.effective_message.reply_text(
            f"*参数错误：* 需要 3 个参数，但收到了 {len(args) -1} 个",
            parse_mode=ParseMode.MARKDOWN,
        )


__help__ = """
进行货币换算

用法：/cash <金额> <源货币> <目标货币>
示例：/cash 100 USD CNY
"""

CONVERTER_HANDLER = CommandHandler("cash", convert, run_async=True)
dispatcher.add_handler(CONVERTER_HANDLER)
__command_list__ = ["cash"]

__handlers__ = [CONVERTER_HANDLER]

__mod_name__ = "汇率换算"
