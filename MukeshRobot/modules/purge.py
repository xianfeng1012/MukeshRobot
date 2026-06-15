import time

from telethon import events

from MukeshRobot import telethn,pbot
from MukeshRobot.modules.helper_funcs.telethn.chatstatus import (
    can_delete_messages,
    user_is_admin,
)


async def purge_messages(event):
    start = time.perf_counter()
    if event.from_id is None:
        return

    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("此命令仅限管理员使用")
        return

    if not await can_delete_messages(message=event):
        await event.reply("无法删除该消息")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply("请回复一条消息，以指定批量删除的起始位置。")
        return
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    try:
        await event.client.delete_messages(event.chat_id, messages)
    except:
        pass
    time_ = time.perf_counter() - start
    text = f"批量删除完成，耗时 {time_:0.2f} 秒\n够快吧 😎"
    await event.respond(text, parse_mode="markdown")


async def delete_messages(event):
    if event.from_id is None:
        return

    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("此命令仅限管理员使用")
        return

    if not await can_delete_messages(message=event):
        await event.reply("无法删除该消息")
        return

    message = await event.get_reply_message()
    if not message:
        await event.reply("请回复一条需要删除的消息。")
        return
    chat = await event.get_input_chat()
    del_message = [message, event.message]
    await event.client.delete_messages(chat, del_message)
async def spurge_messages(event):
    if event.from_id is None:
        return
    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("此命令仅限管理员使用")
        return

    if not await can_delete_messages(message=event):
        await event.reply("无法删除该消息")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply("请回复一条消息，以指定批量删除的起始位置。")
        return
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    try:
        await event.client.delete_messages(event.chat_id, messages)
    except:
        pass

__help__ = """
 ❍ /del *:* 删除你所回复的那条消息
 ❍ /purge *:* 批量删除从当前消息到所回复消息之间的全部消息
 ❍ /purge <整数 x> *:* 删除所回复的消息及其之后的 x 条消息
 ❍ /spurge *:* 静默批量删除从当前消息到所回复消息之间的全部消息
"""

PURGE_HANDLER = purge_messages, events.NewMessage(pattern="^[!/]purge$")

DEL_HANDLER = delete_messages, events.NewMessage(pattern="^[!/]del$")
SPURGE_HANDLER = spurge_messages, events.NewMessage(pattern="^[!/]spurge$")
telethn.add_event_handler(*PURGE_HANDLER)
telethn.add_event_handler(*DEL_HANDLER)
telethn.add_event_handler(*SPURGE_HANDLER)
__mod_name__ = "批量删除"
__command_list__ = ["del", "purge","spurge"]
__handlers__ = [PURGE_HANDLER, DEL_HANDLER,SPURGE_HANDLER]
