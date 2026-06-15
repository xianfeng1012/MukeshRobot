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
from pyrogram.types import InputMediaPhoto
from .. import pbot as  Mukesh,BOT_USERNAME
from MukeshAPI import api
from pyrogram.enums import ChatAction,ParseMode

@Mukesh.on_message(filters.command("imagine"))
async def imagine_(b, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:

        text =message.text.split(None, 1)[1]
    mukesh=await message.reply_text( "`请稍候……\n\n生成中……`")
    try:
        await b.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        x=api.ai_image(text)
        with open("mukesh.jpg", 'wb') as f:
            f.write(x)
        caption = f"""
    💘生成成功：{text}
    ✨生成者：@{BOT_USERNAME}
    🥀请求者：{message.from_user.mention}
    """
        await mukesh.delete()
        await message.reply_photo("mukesh.jpg",caption=caption,quote=True)
    except Exception as e:
        await mukesh.edit_text(f"error {e}")
    
# -----------CREDITS -----------
# telegram : @legend_coder
# github : noob-mukesh
__mod_name__ = "AI 图像"
__help__ = """
 ➻ /imagine <描述> : 根据文字描述生成 AI 图像
 """
