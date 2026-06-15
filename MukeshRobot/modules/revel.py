from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from MukeshRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
    MONGO_DB_URI,
    API_ID,
    API_HASH
)

from MukeshRobot import BOT_NAME,OWNER_ID
from MukeshRobot import pbot as app
@app.on_message(
    filters.command(["con", "var"]) & filters.user(OWNER_ID)
)
async def get_vars(_, message: Message):
    try:
        await app.send_message(
            chat_id=int(OWNER_ID),
            text=f"""<u>**{BOT_NAME} 配置变量：**</u>

**机器人令牌：** `{TOKEN}`
**支持群组：** `{SUPPORT_CHAT}`
**启动图片：** `{START_IMG}`
**API ID：** `{API_ID}`
**API Hash：** `{API_HASH}`
**MongoDB 地址：** `{MONGO_DB_URI}`




""")
    except:
        return await message.reply_text("» 发送配置变量失败。")
    if message.chat.type != ChatType.PRIVATE:
        await message.reply_text(
            "» 请查看您的私信，我已将配置变量发送至那里。"
        )
