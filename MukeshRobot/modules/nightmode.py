from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import functions, types
from telethon.tl.types import ChatBannedRights
from telethon import TelegramClient, events, Button
from MukeshRobot import (
    BOT_NAME,
    BOT_USERNAME)
from MukeshRobot import telethn as tbot
from MukeshRobot.events import register
from MukeshRobot.modules.sql.night_mode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)
openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=False,
    pin_messages=False,
    change_info=False,
)
button_row = [
        [Button.url('Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ', f'https://t.me/{BOT_USERNAME}?startgroup=new')]
    ]
@register(pattern="^/nightmode")
async def close_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("🤦🏻‍♂️您不是管理员，无法使用此命令……")
            return

    if not event.is_group:
        await event.reply("夜间模式只能在群组中启用。")
        return
    if is_nightmode_indb(str(event.chat_id)):
        await event.reply("该群组已启用夜间模式")
        return
    add_nightmode(str(event.chat_id))
    await event.reply(
        f"已添加群组：{event.chat.title} \nID：{event.chat_id} 到数据库。\n**该群组将在 12:00 AM（IST）关闭，06:00 AM（IST）开放**",
       buttons=button_row )


@register(pattern="^/rmnight")
async def disable_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("🤦🏻‍♂️您不是管理员，无法使用此命令……")
            return

    if not event.is_group:
        await event.reply("夜间模式只能在群组中禁用。")
        return
    if not is_nightmode_indb(str(event.chat_id)):
        await event.reply("该群组尚未启用夜间模式")
        return
    rmnightmode(str(event.chat_id))
    await event.reply(
        f"已从数据库移除群组：{event.chat.title} \nID：{event.chat_id}"
    )


async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                f"现在是 12:00 AM，群组将关闭至 6:00 AM。\n夜间模式已启动！\n**由 {BOT_NAME} 提供支持**",buttons=button_row)
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=hehes
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴄʟᴏꜱᴇ ɢʀᴏᴜᴘ {warner} - {e}")


# Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()


async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                f"现在是 06:00 AM，群组已开放。\n**由 {BOT_NAME} 提供支持**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴏᴘᴇɴ ɢʀᴏᴜᴘ {warner.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=6, minute=1)
scheduler.start()

__help__ = """
*仅限管理员*

 ❍ /nightmode *：* 将群组添加到夜间模式列表
 ❍ /rmnight *：* 将群组从夜间模式列表中移除

*注意：* 夜间模式群组将在 12:00 AM（IST）自动关闭，在 6:00 AM（IST）自动开放，以防止夜间刷屏。
"""

__mod_name__ = "夜间模式"
