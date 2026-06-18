"""
GroupBot 主程序
群管理机器人 - 负责进群欢迎、验证、屏蔽垃圾等功能
"""
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from config import GROUP_BOT_TOKEN, LOG_LEVEL, LOG_FILE
from handlers import (
    handle_new_member, handle_channel_verify, moderate_message,
    graduate_probation_users, handle_member_left, cmd_setwelcome, cmd_toggleverify,
    cmd_togglespam, get_group_settings, cleanup_group_command, admin_only,
    reply_autodel
)

# ============ 日志配置 ============
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============ 命令处理 ============
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始命令"""
    await reply_autodel(
        update, context,
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
    await reply_autodel(
        update, context,
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

        # 读取本群设置
        settings = await get_group_settings(chat.id)
        verify_enabled = settings.get('verify_enabled', True)
        spam_enabled = settings.get('spam_enabled', True)
        has_welcome = bool(settings.get('welcome_text'))

        await reply_autodel(
            update, context,
            f"📊 *群组统计*\n\n"
            f"群组名: {chat_obj.title}\n"
            f"成员数: {member_count}\n"
            f"ID: `{chat.id}`\n\n"
            f"功能状态:\n"
            f"{'✅ 自定义' if has_welcome else '✅ 默认'} 欢迎消息\n"
            f"{'✅' if verify_enabled else '❌'} 身份验证\n"
            f"{'✅' if spam_enabled else '❌'} 垃圾过滤",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        await reply_autodel(update, context, f"❌ 获取统计信息失败: {e}")


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
    # 斜杠命令：群内仅管理员有效（私聊不限制），普通群友用汉字命令
    application.add_handler(CommandHandler("start", admin_only(cmd_start)))
    application.add_handler(CommandHandler("help", admin_only(cmd_help)))
    application.add_handler(CommandHandler("stats", admin_only(cmd_stats)))
    application.add_handler(CommandHandler("setwelcome", admin_only(cmd_setwelcome)))
    application.add_handler(CommandHandler("toggleverify", admin_only(cmd_toggleverify)))
    application.add_handler(CommandHandler("togglespam", admin_only(cmd_togglespam)))

    # 汉字命令（需在 moderate_message 之前注册，否则会被它在同一 handler group 抢先处理）
    # 查询类所有人可用；管理类(设置欢迎/验证开关/过滤开关)内部仍校验管理员
    application.add_handler(MessageHandler(filters.Regex(r'^\s*群帮助\s*$'), cmd_help))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*群统计\s*$'), cmd_stats))
    application.add_handler(MessageHandler(filters.Regex(r'^设置欢迎(\s|$)'), cmd_setwelcome))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*验证开关\s*$'), cmd_toggleverify))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*过滤开关\s*$'), cmd_togglespam))

    # 消息处理（始终注册，运行时按群设置决定行为）
    # 新成员：欢迎 + 可选验证
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    # 关注频道验证按钮回调
    application.add_handler(CallbackQueryHandler(handle_channel_verify, pattern='^cv_'))
    # 消息审查：删除非管理员的链接/转发（群内所有非命令、非系统消息）
    application.add_handler(MessageHandler(
        filters.ChatType.GROUPS & ~filters.COMMAND & ~filters.StatusUpdate.ALL,
        moderate_message
    ))

    # 成员离开
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_member_left))

    # 群内所有用户斜杠命令 2 分钟后自动删除（独立 handler group，不影响上面的命令处理）
    application.add_handler(
        MessageHandler(filters.COMMAND & filters.ChatType.GROUPS, cleanup_group_command),
        group=1
    )

    # 定时任务：观察期满3天自动解锁媒体权限（每小时扫描一次）
    application.job_queue.run_repeating(graduate_probation_users, interval=3600, first=60)

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
