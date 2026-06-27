from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters

from MukeshRobot import dispatcher
from MukeshRobot.modules.disable import DisableAbleCommandHandler
from MukeshRobot.modules.helper_funcs.chat_status import user_admin

MARKDOWN_HELP = f"""
Markdown 是 Telegram 支持的非常强大的格式化工具。{dispatcher.bot.first_name} 有一些增强功能，\n
以确保保存的消息能被正确解析，并允许你创建按钮。

• <code>_斜体_</code>：用 '_' 包裹文字可产生斜体效果
• <code>*粗体*</code>：用 '*' 包裹文字可产生粗体效果
• <code>`代码`</code>：用 '`' 包裹文字可产生等宽字体，即"code"格式
• <code>[显示文字](链接地址)</code>：这将创建一个超链接，消息中只显示 <code>显示文字</code>，\n
点击后将打开 <code>链接地址</code> 对应的页面。
<b>示例：</b><code>[测试](example.com)</code>

• <code>[按钮文字](buttonurl:某链接)</code>：这是一个特殊增强功能，允许用户在 Markdown 中添加 Telegram \n
按钮。<code>按钮文字</code> 是按钮上显示的内容，<code>某链接</code> \n
是点击后打开的链接。
<b>示例：</b> <code>[这是一个按钮](buttonurl://google.com)</code>

如果你想在同一行放多个按钮，使用 :same，如下所示：
<code>[按钮一](buttonurl://google.com)
[按钮二](buttonurl://google.com:same )</code>
这将在同一行创建两个按钮，而不是每行一个。

请注意，你的消息<b>必须</b>包含除按钮之外的一些文字内容！
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "试着将以下消息转发给我，你就会明白了，另外可使用 #test！"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "请在私信中联系我",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown 帮助",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


__help__ = """
*可用命令：*
*Markdown：*
 ❍ /markdownhelp*:* 快速了解 Telegram 中 Markdown 的使用方法 - 仅限在私信中使用
*表情回应：*
 ❍ /react *:* 随机表情回应
*Urban Dictionary：*
 ❍ /ud <词语>*:* 查询该词语或表达的俚语含义
*维基百科：*
 ❍ /wiki <关键词>*:* 搜索维基百科
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)

__mod_name__ = "杂项"
__command_list__ = ["id", "echo"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
]
