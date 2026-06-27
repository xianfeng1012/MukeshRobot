from datetime import datetime

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from MukeshRobot import OWNER_ID as owner_id
from MukeshRobot import SUPPORT_CHAT as log,BOT_NAME,START_IMG
from MukeshRobot import pbot as Client
from MukeshRobot.utils.errors import capture_err


def content(msg: Message) -> [None, str]:
    text_to_return = msg.text

    if msg.text is None:
        return None
    if " " in text_to_return:
        try:
            return msg.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None


@Client.on_message(filters.command("bug"))
@capture_err
async def bug(_, msg: Message):
    if msg.chat.username:
        chat_username = f"@{msg.chat.username}/`{msg.chat.id}`"
    else:
        chat_username = f"私人群组/`{msg.chat.id}`"

    bugs = content(msg)
    user_id = msg.from_user.id
    mention = (
        "[" + msg.from_user.first_name + "](tg://user?id=" + str(msg.from_user.id) + ")"
    )
    datetimes_fmt = "%d-%m-%Y"
    datetimes = datetime.utcnow().strftime(datetimes_fmt)

    

    bug_report = f"""
**#问题反馈 : ** **tg://user?id={owner_id}**

**反馈者 : ** **{mention}**
**用户 ID : ** **{user_id}**
**群组 : ** **{chat_username}**

**问题描述 : ** **{bugs}**

**时间戳 : ** **{datetimes}**"""

    if msg.chat.type == "private":
        await msg.reply_text("<b>» 此命令仅限群组中使用。</b>")
        return

    if user_id == owner_id:
        if bugs:
            await msg.reply_text(
                "<b>» 你在逗我吗 🤣，你就是机器人的主人。</b>",
            )
            return
        else:
            await msg.reply_text("主人！")
    elif user_id != owner_id:
        if bugs:
            await msg.reply_text(
                f"<b>问题反馈：{bugs}</b>\n\n"
                "<b>» 问题已成功反馈至支持群组！</b>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• 关闭 •", callback_data=f"close_reply")]]
                ),
            )
            await Client.send_photo(
                log,
                photo=START_IMG,
                caption=f"{bug_report}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("• 查看问题 •", url=f"{msg.link}")],
                        [
                            InlineKeyboardButton(
                                "• 关闭 •", callback_data="close_send_photo"
                            )
                        ],
                    ]
                ),
            )
        else:
            await msg.reply_text(
                f"<b>» 请提供问题描述内容！</b>",
            )


@Client.on_callback_query(filters.regex("close_reply"))
async def close_reply(msg, CallbackQuery):
    await CallbackQuery.message.delete()


@Client.on_callback_query(filters.regex("close_send_photo"))
async def close_send_photo(_, CallbackQuery):
    is_Admin = await Client.get_chat_member(
        CallbackQuery.message.chat.id, CallbackQuery.from_user.id
    )
    if not is_Admin.can_delete_messages:
        return await CallbackQuery.answer(
            "你没有权限关闭此消息。", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()


__help__ = """
*反馈问题*
 ❍ /bug *：* 向支持群组反馈一个问题。
"""
__mod_name__ = "反馈问题"
