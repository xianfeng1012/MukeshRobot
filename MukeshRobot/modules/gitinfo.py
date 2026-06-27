from aiohttp import ClientSession
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from MukeshRobot import pbot
from MukeshRobot.utils.errors import capture_err


@pbot.on_message(filters.command(["github","git"]))
@capture_err
async def github(_, message):
    if len(message.command) != 2:
        return await message.reply_text("/github {username} \n`/github Noob-Mukesh`")
    username = message.text.split(None, 1)[1]
    URL = f"https://api.github.com/users/{username}"
    async with ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                return await message.reply_text("404")
            result = await request.json()
            try:
                url = result["html_url"]
                name = result["name"]
                company = result["company"]
                bio = result["bio"]
                created_at = result["created_at"]
                avatar_url = result["avatar_url"]
                blog = result["blog"]
                location = result["location"]
                repositories = result["public_repos"]
                followers = result["followers"]
                following = result["following"]
                global Mukesh
                Mukesh = [[
            InlineKeyboardButton(text="个人主页", url=url),
            InlineKeyboardButton("关闭",callback_data="close_reply")
            ]]
                caption = f"""**{name} 的 GitHub 信息**
**用户名：** `{username}`
**简介：** `{bio}`
**公司：** `{company}`
**注册时间：** `{created_at}`
**仓库数：** `{repositories}`
**博客：** `{blog}`
**位置：** `{location}`
**粉丝数：** `{followers}`
**关注数：** `{following}`"""
            except Exception as e:
                await message.reply(f"#ERROR {e}")
                  
    await message.reply_photo(photo=avatar_url, caption=caption,reply_markup=InlineKeyboardMarkup(Mukesh))


__mod_name__ = "Git 信息"

__help__ = """
查询 GitHub 用户的个人资料信息。

 ❍ /github <用户名> *:* 获取指定 GitHub 用户的信息。
"""
