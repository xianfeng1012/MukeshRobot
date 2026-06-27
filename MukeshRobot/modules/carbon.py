from pyrogram import filters

from MukeshRobot import pbot
from MukeshRobot.utils.errors import capture_err
from MukeshRobot.utils.functions import make_carbon


@pbot.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if message.reply_to_message:
        if message.reply_to_message.text:
            txt = message.reply_to_message.text
        else:
            return await message.reply_text("请回复一条消息或提供文本内容。")
    else:
        try:
            txt = message.text.split(None, 1)[1]
        except IndexError:
            return await message.reply_text("请回复一条消息或提供文本内容。")
    m = await message.reply_text("正在生成代码美化图片……")
    carbon = await make_carbon(txt)
    await m.edit_text("正在上传生成的图片……")
    await pbot.send_photo(
        message.chat.id,
        photo=carbon,
        caption=f"» 请求者：{message.from_user.mention}",
    )
    await m.delete()
    carbon.close()

__mod_name__ = "代码美化"

__help__ = """

将给定文本生成代码美化图片并发送给您。

❍ /carbon *:* 回复一条文本消息或直接携带文本，生成代码美化图片。

 """
