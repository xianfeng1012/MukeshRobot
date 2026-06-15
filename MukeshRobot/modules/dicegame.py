from pyrogram import Client, enums, filters
#from config import *
import asyncio
from MukeshRobot import pbot as mukesh

from pyrogram.handlers import MessageHandler


@mukesh.on_message(filters.command("dice"))
async def dice(bot, message):
    x=await bot.send_dice(message.chat.id)
    m=x.dice.value
    await message.reply_text(f"{message.from_user.mention} 你的得分是：{m}",quote=True)

@mukesh.on_message(filters.command("dart"))
async def dart(bot, message):
    x=await bot.send_dice(message.chat.id, "🎯")
    m=x.dice.value
    await message.reply_text(f"{message.from_user.mention} 你的得分是：{m}",quote=True)

@mukesh.on_message(filters.command("basket"))
async def basket(bot, message):
    x=await bot.send_dice(message.chat.id, "🏀")
    m=x.dice.value
    await message.reply_text(f"{message.from_user.mention} 你的得分是：{m}",quote=True)
@mukesh.on_message(filters.command("jackpot"))
async def basket(bot, message):
    x=await bot.send_dice(message.chat.id, "🎰")
    m=x.dice.value
    await message.reply_text(f"{message.from_user.mention} 你的得分是：{m}",quote=True)
@mukesh.on_message(filters.command("ball"))
async def basket(bot, message):
    x=await bot.send_dice(message.chat.id, "🎳")
    m=x.dice.value
    await message.reply_text(f"{message.from_user.mention} 你的得分是：{m}",quote=True)
@mukesh.on_message(filters.command("football"))
async def basket(bot, message):
    x=await bot.send_dice(message.chat.id, "⚽")
    m=x.dice.value
    await message.reply_text(f"{message.from_user.mention} 你的得分是：{m}",quote=True)
__help__ = """
 用表情玩游戏：
/dice - 掷骰子 🎲
/dart - 飞镖 🎯
/basket - 篮球 🏀
/ball - 保龄球 🎳
/football - 足球 ⚽
/jackpot - 老虎机 🎰
 """

__mod_name__ = "骰子游戏"
