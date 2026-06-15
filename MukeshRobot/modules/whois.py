from datetime import datetime

from pyrogram import filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.types import Message, User

from MukeshRobot import pbot


def ReplyCheck(message: Message):
    reply_id = None

    if message.reply_to_message:
        reply_id = message.reply_to_message.message_id

    elif not message.from_user.is_self:
        reply_id = message.message_id

    return reply_id


infotext = (
    "[{full_name}](tg://user?id={user_id})\n\n"
    " ➻ 用户 ID: `{user_id}`\n"
    " ➻ 名字: `{first_name}`\n"
    " ➻ 姓氏: `{last_name}`\n"
    " ➻ 用户名: `@{username}`\n"
    " ➻ 最后上线: `{last_online}`"
)


def LastOnline(user: User):
    if user.is_bot:
        return ""
    elif user.status == "recently":
        return "最近在线"
    elif user.status == "within_week":
        return "一周内在线"
    elif user.status == "within_month":
        return "一个月内在线"
    elif user.status == "long_time_ago":
        return "很久以前 :("
    elif user.status == "online":
        return "当前在线"
    elif user.status == "offline":
        return datetime.fromtimestamp(user.status.date).strftime(
            "%a, %d %b %Y, %H:%M:%S"
        )


def FullName(user: User):
    return user.first_name + " " + user.last_name if user.last_name else user.first_name


@pbot.on_message(filters.command("whois"))
async def whois(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_users(get_user)
    except PeerIdInvalid:
        await message.reply("未找到该用户。")
        return
    desc = await client.get_chat(get_user)
    desc = desc.description
    await message.reply_text(
        infotext.format(
            full_name=FullName(user),
            user_id=user.id,
            user_dc=user.dc_id,
            first_name=user.first_name,
            last_name=user.last_name if user.last_name else "",
            username=user.username if user.username else "",
            last_online=LastOnline(user),
            bio=desc if desc else "`ᴇᴍᴩᴛʏ.`",
        ),
        disable_web_page_preview=True,
    )
