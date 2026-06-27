import datetime
from typing import List

import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from MukeshRobot import TIME_API_KEY, dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler


def generate_time(to_find: str, findtype: List[str]) -> str:
    data = requests.get(
        f"https://api.timezonedb.com/v2.1/list-time-zone"
        f"?key={TIME_API_KEY}"
        f"&format=json"
        f"&fields=countryCode,countryName,zoneName,gmtOffset,timestamp,dst"
    ).json()

    for zone in data["zones"]:
        for eachtype in findtype:
            if to_find in zone[eachtype].lower():
                country_name = zone["countryName"]
                country_zone = zone["zoneName"]
                country_code = zone["countryCode"]

                if zone["dst"] == 1:
                    daylight_saving = "Yes"
                else:
                    daylight_saving = "No"

                date_fmt = r"%d-%m-%Y"
                time_fmt = r"%H:%M:%S"
                day_fmt = r"%A"
                gmt_offset = zone["gmtOffset"]
                timestamp = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(seconds=gmt_offset)
                current_date = timestamp.strftime(date_fmt)
                current_time = timestamp.strftime(time_fmt)
                current_day = timestamp.strftime(day_fmt)

                break

    try:
        result = (
            f"<b>国家：</b> <code>{country_name}</code>\n"
            f"<b>时区名称：</b> <code>{country_zone}</code>\n"
            f"<b>国家代码：</b> <code>{country_code}</code>\n"
            f"<b>夏令时：</b> <code>{daylight_saving}</code>\n"
            f"<b>星期：</b> <code>{current_day}</code>\n"
            f"<b>当前时间：</b> <code>{current_time}</code>\n"
            f"<b>当前日期：</b> <code>{current_date}</code>\n"
            '<b>时区列表：</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">点击查看</a>'
        )
    except:
        result = None

    return result


def gettime(update: Update, context: CallbackContext):
    message = update.effective_message

    try:
        query = message.text.strip().split(" ", 1)[1]
    except:
        message.reply_text("请提供国家名称、缩写或时区名称。")
        return
    send_message = message.reply_text(
        f"正在查询 <b>{query}</b> 的时区信息……", parse_mode=ParseMode.HTML
    )

    query_timezone = query.lower()
    if len(query_timezone) == 2:
        result = generate_time(query_timezone, ["countryCode"])
    else:
        result = generate_time(query_timezone, ["zoneName", "countryName"])

    if not result:
        send_message.edit_text(
            f"未找到 <b>{query}</b> 的时区信息\n"
            '<b>所有时区：</b> <a href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">点击查看</a>',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    send_message.edit_text(
        result, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


__help__ = """
 ❍ /time <查询内容>*:* 获取某个时区的详细信息。
*可用查询方式：* 国家代码/国家名称/时区名称

 ❍ ⏰ [时区列表](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

💡 示例：/time CN *:* 将显示中国的当前时间和日期。
"""

TIME_HANDLER = DisableAbleCommandHandler("time", gettime, run_async=True)

dispatcher.add_handler(TIME_HANDLER)

__mod_name__ = "时间查询"
__command_list__ = ["time"]
__handlers__ = [TIME_HANDLER]
