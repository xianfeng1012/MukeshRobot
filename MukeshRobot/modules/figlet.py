from pyrogram import filters
import asyncio
import pyfiglet 
from random import choice
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.handlers import MessageHandler
from .. import pbot as Client
def figle(text):
    x = pyfiglet.FigletFont.getFonts()
    font = choice(x)
    figled = str(pyfiglet.figlet_format(text,font=font))
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="换一个", callback_data="figlet"),InlineKeyboardButton(text="关闭", callback_data="close_reply")]])
    return figled, keyboard

@Client.on_message(filters.command("figlet"))
async def echo(bot, message):
    global text
    try:
        text = message.text.split(' ',1)[1]
    except IndexError:
        return await message.reply_text("示例：\n\n`/figlet Mukesh`")
    kul_text, keyboard = figle(text)
    await message.reply_text(f"这是你的艺术字：\n<pre>{kul_text}</pre>", quote=True, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("figlet"))
async def figlet_handler(Client, query: CallbackQuery):
  try:
      kul_text, keyboard = figle(text)
      await query.message.edit_text(f"这是你的艺术字：\n<pre>{kul_text}</pre>", reply_markup=keyboard)
  except Exception as e : 
      await message.reply(e)
__mod_name__ = "艺术字"
__help__="""
❍ /figlet*：* 将给定文本生成 ASCII 艺术字
示例：\n\n`/figlet Mukesh`"""
