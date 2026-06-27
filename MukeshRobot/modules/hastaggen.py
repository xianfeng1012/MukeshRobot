import requests
from MukeshRobot import pbot as mukesh
from pyrogram import filters

@mukesh.on_message(filters.command("hastag"))
async def hastag(bot, message):
    
    try:
        text = message.text.split(' ',1)[1]
        res = requests.get(f"https://mukesh-api.vercel.app/hastag?query={text}").json()["results"]

    except IndexError:
        return await message.reply_text("示例：\n\n`/hastag python`")
        
    
    await message.reply_text(f"你的话题标签如下：\n<pre>{res}</pre>", quote=True)
    
__mod_name__ = "标签生成"
__help__= """
**你可以使用此话题标签生成器，根据一个关键词生成前 30 个及更多相关标签。**
° /hastag 输入词语即可生成话题标签。
°示例：` /hastag python `"""

