from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

import MukeshRobot.modules.sql.global_bans_sql as gban_sql
import MukeshRobot.modules.sql.users_sql as user_sql
from MukeshRobot import DEV_USERS, OWNER_ID, dispatcher
from MukeshRobot.modules.helper_funcs.chat_status import dev_plus


def get_invalid_chats(update: Update, context: CallbackContext, remove: bool = False):
    bot = context.bot
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% 正在获取无效群组……"
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar, chat_id, progress_message.message_id
                    )
                except:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        sleep(0.1)
        try:
            bot.get_chat(cid, timeout=60)
        except (BadRequest, Unauthorized):
            kicked_chats += 1
            chat_list.append(cid)
        except:
            pass

    try:
        progress_message.delete()
    except:
        pass

    if not remove:
        return kicked_chats
    else:
        for muted_chat in chat_list:
            sleep(0.1)
            user_sql.rem_chat(muted_chat)
        return kicked_chats


def get_invalid_gban(update: Update, context: CallbackContext, remove: bool = False):
    bot = context.bot
    banned = gban_sql.get_gban_list()
    ungbanned_users = 0
    ungban_list = []

    for user in banned:
        user_id = user["user_id"]
        sleep(0.1)
        try:
            bot.get_chat(user_id)
        except BadRequest:
            ungbanned_users += 1
            ungban_list.append(user_id)
        except:
            pass

    if not remove:
        return ungbanned_users
    else:
        for user_id in ungban_list:
            sleep(0.1)
            gban_sql.ungban_user(user_id)
        return ungbanned_users


@dev_plus
def dbcleanup(update: Update, context: CallbackContext):
    msg = update.effective_message

    msg.reply_text("正在获取无效群组数量……")
    invalid_chat_count = get_invalid_chats(update, context)

    msg.reply_text("正在获取无效全局封禁数量……")
    invalid_gban_count = get_invalid_gban(update, context)

    reply = f"无效群组总数：{invalid_chat_count}\n"
    reply += f"无效全局封禁用户总数：{invalid_gban_count}"

    buttons = [[InlineKeyboardButton("清理数据库", callback_data="db_cleanup")]]

    update.effective_message.reply_text(
        reply, reply_markup=InlineKeyboardMarkup(buttons)
    )


def callback_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    admin_list = [OWNER_ID] + DEV_USERS

    bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat":
        if query.from_user.id in admin_list:
            bot.editMessageText("正在退出群组……", chat_id, message.message_id)
            chat_count = get_muted_chats(update, context, True)
            bot.sendMessage(chat_id, f"已退出 {chat_count} 个群组。")
        else:
            query.answer("你没有权限执行此操作。")
    elif query_type == "db_cleanup":
        if query.from_user.id in admin_list:
            bot.editMessageText("正在清理数据库……", chat_id, message.message_id)
            invalid_chat_count = get_invalid_chats(update, context, True)
            invalid_gban_count = get_invalid_gban(update, context, True)
            reply = "已从数据库中清理 {} 个无效群组和 {} 个无效全局封禁用户。".format(
                invalid_chat_count, invalid_gban_count
            )
            bot.sendMessage(chat_id, reply)
        else:
            query.answer("你没有权限执行此操作。")


DB_CLEANUP_HANDLER = CommandHandler("dbcleanup", dbcleanup, run_async=True)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*", run_async=True)

dispatcher.add_handler(DB_CLEANUP_HANDLER)
dispatcher.add_handler(BUTTON_HANDLER)

__mod_name__ = "数据库"
__handlers__ = [DB_CLEANUP_HANDLER, BUTTON_HANDLER]
