import asyncio
import datetime
import re
from datetime import datetime

from telethon import custom, events

from MukeshRobot import telethn as bot,BOT_NAME
from MukeshRobot import telethn as tgbot
from MukeshRobot.events import register

edit_time = 5
f""" ======================={BOT_NAME}====================== """
file1 = "https://telegra.ph/file/9a85d0a873e2dd80d278d.jpg"
file2 = "https://telegra.ph/file/9e7815284031452afa9e5.jpg"
file3 = "https://telegra.ph/file/dcc5e003287f69acea368.jpg"
file4 = "https://telegra.ph/file/ed1ce7fee94f46b0f671e.jpg"
file5 = "https://telegra.ph/file/701028ce085ecfa961a36.jpg"
""" ======================={BOT_NAME}====================== """


@register(pattern="/myinfo")
async def proboyx(event):
    await event.get_chat()
    datetime.utcnow()
    firstname = event.sender.first_name
    button = [[custom.Button.inline("查看信息", data="informations")]]
    on = await bot.send_file(
        event.chat_id,
        file=file2,
        caption=f"嗨 {firstname}，\n点击下方按钮\n查看你的个人信息",
        buttons=button,
    )

    await asyncio.sleep(edit_time)
    ok = await bot.edit_message(event.chat_id, on, file=file3, buttons=button)

    await asyncio.sleep(edit_time)
    ok2 = await bot.edit_message(event.chat_id, ok, file=file5, buttons=button)

    await asyncio.sleep(edit_time)
    ok3 = await bot.edit_message(event.chat_id, ok2, file=file1, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file4, buttons=button)

    await asyncio.sleep(edit_time)
    ok4 = await bot.edit_message(event.chat_id, ok3, file=file2, buttons=button)

    await asyncio.sleep(edit_time)
    ok5 = await bot.edit_message(event.chat_id, ok4, file=file1, buttons=button)

    await asyncio.sleep(edit_time)
    ok6 = await bot.edit_message(event.chat_id, ok5, file=file3, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file5, buttons=button)

    await asyncio.sleep(edit_time)
    ok7 = await bot.edit_message(event.chat_id, ok6, file=file4, buttons=button)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"information")))
async def callback_query_handler(event):
    try:
        boy = event.sender_id
        PRO = await bot.get_entity(boy)
        LILIE = f"由 {BOT_NAME} 提供支持\n\n"
        LILIE += f"名：{PRO.first_name} \n" + (f"姓：{PRO.last_name}\n" if PRO.last_name else '')
        LILIE += f"是否机器人：{PRO.bot} \n"
        LILIE += f"是否受限：{PRO.restricted} \n"
        LILIE += f"用户 ID：{boy}\n"
        LILIE += f"用户名：@{PRO.username}\n" if PRO.username else f"用户名：`{PRO.username}`\n"
        await event.answer(LILIE, alert=True)
    except Exception as e:
        await event.reply(f"{e}")


__command_list__ = ["myinfo"]

