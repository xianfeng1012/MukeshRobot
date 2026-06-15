"""MIT License

Copyright (c) 2023-24 Noob-Mukesh

          GITHUB: NOOB-MUKESH
          TELEGRAM: @MR_SUKKUN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
from pyrogram import filters
from pyrogram.types import  Message
from pyrogram.enums import ChatAction

from .. import pbot as  Mukesh,BOT_USERNAME
import requests


@Mukesh.on_message(filters.command("qrcode"))
async def qrcode_(_, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:
        text =message.text.split(None, 1)[1]
    m =await message.reply_text( "`请稍候……\n\n正在生成二维码……`")
    write = requests.get(f"https://mukesh-api.vercel.app/qrcode?query={text}").json()["results"]

    caption = f"""
二维码生成成功 💘
✨ **生成者：** @{BOT_USERNAME}
🥀 **请求者：** {message.from_user.mention}
"""
    await m.delete()
    await message.reply_photo(photo=write,caption=caption)
# -----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
__mod_name__ = "二维码"
__help__ = """
 ➻ /qrcode <文本> : 输入文字内容，生成对应二维码
 """
