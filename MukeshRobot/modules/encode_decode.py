import requests
from .. import pbot as Mukesh,BOT_NAME,BOT_USERNAME
import time
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
@Mukesh.on_message(filters.command(["password"]))
async def passwordgen(bot, message):
    
    try:
        
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            return await message.reply_text(
            "示例：**\n\n`/password <长度>`")
        else:
            a = message.text.split(' ', 1)[1]
            response = requests.get(f'https://mukesh-api.vercel.app/password?num={a}')
            x=response.json()["results"]

            await message.reply_text(f"您的密码：` {x}`", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**错误：{e} ")
@Mukesh.on_message(filters.command(["morseencode"]))
async def morse_en(bot, message):
    
    try:
        
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            return await message.reply_text(
            "示例：**\n\n`/morseencode <内容>`")
        else:
            a = message.text.split(' ', 1)[1]
            response = requests.get(f'https://mukesh-api.vercel.app/morse/encode?query={a}')
            x=response.json()["results"]

            await message.reply_text(f"`{x}`", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**错误：{e} ")
@Mukesh.on_message(filters.command("morsedecode"))
async def morse_de(bot, message):
    
    try:
        
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            return await message.reply_text(
            "示例：**\n\n`/morsedecode <内容>`")
        else:
            a = message.text.split(' ', 1)[1]
            response = requests.get(f'https://mukesh-api.vercel.app/morse/decode?query={a}')
            x=response.json()["results"]

            await message.reply_text(f"`{x}`", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**错误：{e} ")
@Mukesh.on_message(filters.command(["encode"]))
async def base_en(bot, message):
    
    try:
        
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            return await message.reply_text(
            "示例：**\n\n`/encode <内容>`")
        else:
            a = message.text.split(' ', 1)[1]
            response = requests.get(f'https://mukesh-api.vercel.app/base/encode?query={a}')
            x=response.json()["results"]

            await message.reply_text(f"` {x}`", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**错误：{e} ")
@Mukesh.on_message(filters.command(["decode"]))
async def base_de(bot, message):
    
    try:
        
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            return await message.reply_text(
            "示例：**\n\n`/decode <内容>`")
        else:
            a = message.text.split(' ', 1)[1]
            response = requests.get(f'https://mukesh-api.vercel.app/base/decode?query={a}')
            x=response.json()["results"]

            await message.reply_text(f" `{x}`", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"**错误：{e} ")

__mod_name__ = "编解码"

__help__ = """
编码/解码文本及摩斯密码工具

❍ /encode <内容> *:* Base64 编码文本
❍ /decode <内容> *:* Base64 解码文本
❍ /morseencode <内容> *:* 将文本编码为摩斯密码
❍ /morsedecode <内容> *:* 将摩斯密码解码为文本
❍ /password <长度> *:* 生成指定长度的随机密码
"""
