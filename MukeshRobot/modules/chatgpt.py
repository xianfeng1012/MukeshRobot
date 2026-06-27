import requests
from .. import pbot as Mukesh,BOT_NAME,BOT_USERNAME
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from MukeshAPI import api
@Mukesh.on_message(filters.command(["chatgpt","ai","ask"],  prefixes=["+", ".", "/", "-", "?", "$","#","&"]))
async def chat_gpt(bot, message):
    
    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text(
            "示例：**\n\n`/chatgpt 泰姬陵在哪里？`")
        else:
            a = message.text.split(' ', 1)[1]
            r=api.gemini(a)["results"]
            await message.reply_text(f" {r} \n\n🎉由 @{BOT_USERNAME} 提供支持 ", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**错误：{e} ")

__mod_name__ = "ChatGPT"
__help__ = """
 ChatGPT 可以回答您的问题并展示结果

 ❍ /chatgpt *:* 回复消息或直接输入问题

 """
