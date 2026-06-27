from telethon import Button, events, types
from telethon.errors import ChatAdminRequiredError
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

from MukeshRobot import BOT_ID
from MukeshRobot import DRAGONS as DEVS
from MukeshRobot import OWNER_ID
from MukeshRobot import telethn as Mukesh
from MukeshRobot.events import Mukeshinline
from MukeshRobot.events import register as Mukeshbot
from MukeshRobot.modules.no_sql import fsub_db as db


async def is_admin(chat_id, user_id):
    try:
        p = await Mukesh(GetParticipantRequest(chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipantAdmin) or isinstance(
        p.participant, types.ChannelParticipantCreator
    ):
        return True
    else:
        return False


async def participant_check(channel, user_id):
    try:
        await Mukesh(GetParticipantRequest(channel, int(user_id)))
        return True
    except UserNotParticipantError:
        return False
    except:
        return False


@Mukeshbot(pattern="^/(fsub|Fsub|forcesubscribe|Forcesub|forcesub|Forcesubscribe) ?(.*)")
async def fsub(event):
    if event.is_private:
        return
    if event.is_group:
        perm = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perm.is_admin:
            return await event.reply("你需要是管理员才能执行此操作。")
        if not perm.is_creator:
            return await event.reply(
                "❗ <b>需要群组创建者权限</b> \n<i>你必须是群组创建者才能执行此操作。</i>",
                parse_mode="html",
            )
    try:
        channel = event.text.split(None, 1)[1]
    except IndexError:
        channel = None
    if not channel:
        chat_db = db.fs_settings(event.chat_id)
        if not chat_db:
            await event.reply(
                "<b>❌ 本群未启用强制订阅。</b>", parse_mode="HTML"
            )
        else:
            await event.reply(
                f"强制订阅当前状态：<b>已启用</b>。用户必须加入 <b>@{chat_db.channel}</b> 才能在此发言。",
                parse_mode="html",
            )
    elif channel in ["on", "yes", "y"]:
        await event.reply("❗请指定频道用户名。")
    elif channel in ["off", "no", "n"]:
        await event.reply("**❌ 强制订阅已成功关闭。**")
        db.disapprove(event.chat_id)
    else:
        try:
            channel_entity = await event.client.get_entity(channel)
        except:
            return await event.reply(
                "❗<b>提供的频道用户名无效。</b>", parse_mode="html"
            )
        channel = channel_entity.username
        try:
            if not channel_entity.broadcast:
                return await event.reply("这不是一个有效的频道。")
        except:
            return await event.reply("这不是一个有效的频道。")
        if not await participant_check(channel, BOT_ID):
            return await event.reply(
                f"❗**我不是该频道的管理员**\n我不是 [频道](https://t.me/{channel}) 的管理员。请将我添加为管理员以启用强制订阅。",
                link_preview=False,
            )
        db.add_channel(event.chat_id, str(channel))
        await event.reply(f"✅ **强制订阅已启用**，目标频道：@{channel}。")


@Mukesh.on(events.NewMessage())
async def fsub_n(e):
    if not db.fs_settings(e.chat_id):
        return
    if e.is_private:
        return
    if e.chat.admin_rights:
        if not e.chat.admin_rights.ban_users:
            return
    else:
        return
    if not e.from_id:
        return
    if (
        await is_admin(e.chat_id, e.sender_id)
        or e.sender_id in DEVS
        or e.sender_id == OWNER_ID
    ):
        return
    channel = (db.fs_settings(e.chat_id)).get("channel")
    try:
        check = await participant_check(channel, e.sender_id)
    except ChatAdminRequiredError:
        return
    if not check:
        buttons = [Button.url("加入频道", f"t.me/{channel}")], [
            Button.inline("解除禁言", data="fs_{}".format(str(e.sender_id)))
        ]
        txt = f'<b><a href="tg://user?id={e.sender_id}">{e.sender.first_name}</a></b>，你还<b>未订阅</b>我们的 <b><a href="t.me/{channel}">频道</a></b>❗请先 <b><a href="t.me/{channel}">加入频道</a></b>，然后<b>点击下方按钮</b>以解除禁言。'
        await e.reply(txt, buttons=buttons, parse_mode="html", link_preview=False)
        await e.client.edit_permissions(e.chat_id, e.sender_id, send_messages=False)


@Mukeshinline(pattern=r"fs(\_(.*))")
async def unmute_fsub(event):
    user_id = int(((event.pattern_match.group(1)).decode()).split("_", 1)[1])
    if not event.sender_id == user_id:
        return await event.answer("这个按钮不是给你用的。", alert=True)
    channel = (db.fs_settings(event.chat_id)).get("channel")
    try:
        check = await participant_check(channel, user_id)
    except ChatAdminRequiredError:
        check = False
        return
    if not check:
        return await event.answer(
            "你必须先加入频道，才能解除禁言！", alert=True
        )
    try:
        await event.client.edit_permissions(event.chat_id, user_id, send_messages=True)
    except ChatAdminRequiredError:
        pass
    await event.delete()


__mod_name__ = "强制订阅"

__help__="""
*强制订阅：*

   •➥ *机器人可以对未订阅你频道的成员禁言，直到他们订阅为止*
   •➥ 启用后，我会对未订阅的成员禁言并显示解除禁言按钮，当他们点击按钮时我会为其解除禁言

   •➥ *设置步骤*
   •➥ [将我添加为群组管理员](https://t.me/groupcontrollertgbot?startgroup=new)
   •➥ [将我添加为频道管理员](https://t.me/groupcontrollertgbot?startgroup=new)

    *命令*
   •➥ /fsub 频道用户名 - 开启并设置强制订阅频道。
   •➥ /fsub off - 关闭强制订阅。
   💡 如果你关闭了强制订阅，需要重新运行 /fsub 频道用户名 才能再次启用

"""

