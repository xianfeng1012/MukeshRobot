import secureme
from pyrogram import filters
from MukeshRobot import pbot as mukesh


@mukesh.on_message(filters.command("encrypt"))
async def encyrpt(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("**示例：**\n\n`/encyrpt 你好世界`")
    m = message.text.split(' ',1)[1]
    try:
        Secure = secureme.encrypt(m)

        await message.reply_text(f"`{Secure}`")


    except Exception as e:
        await message.reply_text(f"错误：{e}")

@mukesh.on_message(filters.command("decrypt"))
async def decrypt(bot, message):
    if len(message.command) < 2:
        return await message.reply_text("**示例：**\n\n`/decrypt Nsinf`")
    m = message.text.split(' ',1)[1]
    try:
        Decrypt = secureme.decrypt(m)
        
        await message.reply_text(f"`{Decrypt}`")
        

    except Exception as e:
        await message.reply_text(f"{e}")


__mod_name__ = "加密"

__help__ = """
*文本转换*
 ❍ /encrypt*：* 加密给定的文本
 ❍ /decrypt*：* 解密已加密的文本
 ❍ /encode*：* 编码给定的文本
 ❍ /decode*：* 解码已编码的文本
 ❍ /morseencode*：* 将文本转换为摩斯密码
 ❍ /morsedecode*：* 解码摩斯密码
 ❍ /password *：* 指定长度生成随机密码
 ❍ /uselessfact *：* 生成随机无聊冷知识
"""
