"""
GroupBot 主程序
群管理机器人 - 负责进群欢迎、验证、屏蔽垃圾等功能
"""
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, ContextTypes

from config import (
    GROUP_BOT_TOKEN, LOG_LEVEL, LOG_FILE,
    WELCOME_ENABLED, VERIFICATION_ENABLED, SPAM_FILTER_ENABLED
)
from handlers import (
    handle_new_member, handle_verification_button, filter_spam, handle_member_left
)

# ============ 日志配置 ============
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ 命令处理 ============
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    await update.message.reply_text(
        "👋 你好！我是群管理机器人\n\n"
        "我负责:\n"
        "✅ 欢迎新成员\n"
        "✅ 验证真人身份\n"
        "✅ 屏蔽垃圾消息\n"
        "✅ 屏蔽广告\n\n"
        "请将我添加到你的群组以开始使用"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助命令"""
    await update.message.reply_text(
        "📖 *群管理机器人帮助*\n\n"
        "*管理员命令:*\n"
        "/setwelcome - 设置欢迎消息\n"
        "/toggleverify - 切换验证功能\n"
        "/togglespam - 切换垃圾过滤\n"
        "/stats - 查看群组统计\n\n"
        "*其他:*\n"
        "/start - 开始\n"
        "/help - 帮助",
        parse_mode='Markdown'
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看群组统计"""
    try:
        chat = update.effective_chat

        # 获取群组信息
        chat_obj = await context.bot.get_chat(chat.id)
        member_count = await context.bot.get_chat_member_count(chat.id)

        await update.message.reply_text(
            f"📊 *群组统计*\n\n"
            f"群组名: {chat_obj.title}\n"
            f"成员数: {member_count}\n"
            f"ID: `{chat.id}`\n\n"
            f"功能状态:\n"
            f"{'✅' if WELCOME_ENABLED else '❌'} 欢迎消息\n"
            f"{'✅' if VERIFICATION_ENABLED else '❌'} 身份验证\n"
            f"{'✅' if SPAM_FILTER_ENABLED else '❌'} 垃圾过滤",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        await update.message.reply_text(f"❌ 获取统计信息失败: {e}")


# ============ 应用初始化 ============
async def post_init(application: Application) -> None:
    """应用初始化后的回调"""
    logger.info("GroupBot 已启动")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """错误处理"""
    logger.error(f"GroupBot 发生错误: {context.error}", exc_info=context.error)


def main():
    """主函数"""
    # 检查Token
    if not GROUP_BOT_TOKEN:
        logger.error("GROUP_BOT_TOKEN 未设置")
        sys.exit(1)

    # 创建应用
    application = Application.builder().token(GROUP_BOT_TOKEN).build()

    # 注册处理器
    # 命令处理
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("stats", cmd_stats))

    # 消息处理
    if WELCOME_ENABLED or VERIFICATION_ENABLED:
        application.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_new_member))

    if VERIFICATION_ENABLED:
        application.add_handler(CallbackQueryHandler(handle_verification_button, pattern='^verify_'))

    if SPAM_FILTER_ENABLED:
        application.add_handler(MessageHandler(Filters.text & ~Filters.command, filter_spam))

    # 成员离开
    application.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_member_left))

    # 错误处理
    application.add_error_handler(error_handler)

    # 初始化回调
    application.post_init = post_init

    # 启动
    logger.info("GroupBot 启动中...")
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            stop_signals=[2, 15],  # SIGINT, SIGTERM
            timeout=30,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30
        )
    except KeyboardInterrupt:
        logger.info("GroupBot 被中断")
    except Exception as e:
        logger.error(f"GroupBot 运行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
