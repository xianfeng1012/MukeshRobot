
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from MukeshAPI import api 
from MukeshRobot import pbot as Mukesh
@Mukesh.on_message(filters.command("truth"))
async def truth_(client: Client, message: Message):

    truth =api.truth()
    await message.reply_text(truth)

@Mukesh.on_message(filters.command("dare"))
async def dare_(client: Client, message: Message):

    dare =api.dare()
    await message.reply_text(dare)


__help__ = """
*真心话大冒险*
 ❍ /truth *:* 发送一条随机真心话问题。
 ❍ /dare *:* 发送一条随机大冒险挑战。
"""
__mod_name__ = "真心话大冒险"
