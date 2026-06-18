"""
UserBot 主程序
用户管理机器人 - 负责个人档案、活动记录、统计等功能
"""
import logging
import sys
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, ContextTypes, filters,
)

from config import USER_BOT_TOKEN, LOG_LEVEL, LOG_FILE
from handlers import (
    cmd_profile, cmd_activity, cmd_stats, cmd_privacy, cmd_achievements, admin_only,
    cmd_pointsrules, cmd_guide, cmd_menu, handle_guide_callback,
    handle_join_menu, handle_join_menu_cm,
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
    await update.message.reply_text(
        "👤 *用户管理机器人*\n\n"
        "欢迎使用！我负责:\n"
        "👤 个人档案管理\n"
        "📋 活动记录查询\n"
        "📊 统计数据分析\n"
        "🎖️ 成就展示\n\n"
        "*可用命令:*\n"
        "/profile - 查看个人档案\n"
        "/activity - 活动记录\n"
        "/stats - 统计数据\n"
        "/achievements - 成就展示\n"
        "/privacy - 隐私设置",
        parse_mode='Markdown'
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助命令"""
    await update.message.reply_text(
        "📖 *用户管理机器人帮助*\n\n"
        "*命令列表:*\n"
        "/profile - 👤 查看个人档案和统计\n"
        "/activity - 📋 查看最近活动记录\n"
        "/stats - 📊 查看详细统计数据\n"
        "/achievements - 🎖️ 查看已获得的成就\n"
        "/privacy - 🔐 管理隐私设置\n"
        "/guide - 🧭 群内导航（汉字「导航」）\n"
        "/pointsrules - 📊 积分规则（汉字「积分规则」）\n"
        "/help - ❓ 显示此帮助信息",
        parse_mode='Markdown'
    )


# ============ 应用初始化 ============
async def post_init(application: Application) -> None:
    """应用初始化后的回调"""
    logger.info("UserBot 已启动")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """错误处理"""
    logger.error(f"UserBot 发生错误: {context.error}", exc_info=context.error)


def main():
    """主函数"""
    # 检查Token
    if not USER_BOT_TOKEN:
        logger.error("USER_BOT_TOKEN 未设置")
        sys.exit(1)

    # 创建应用
    application = Application.builder().token(USER_BOT_TOKEN).build()

    # 注册处理器
    # 斜杠命令：群内仅管理员有效（私聊不限制），普通群友用汉字命令
    application.add_handler(CommandHandler("start", admin_only(cmd_start)))
    application.add_handler(CommandHandler("help", admin_only(cmd_help)))
    application.add_handler(CommandHandler("profile", admin_only(cmd_profile)))
    application.add_handler(CommandHandler("activity", admin_only(cmd_activity)))
    application.add_handler(CommandHandler("stats", admin_only(cmd_stats)))
    application.add_handler(CommandHandler("achievements", admin_only(cmd_achievements)))
    application.add_handler(CommandHandler("privacy", admin_only(cmd_privacy)))
    application.add_handler(CommandHandler("pointsrules", admin_only(cmd_pointsrules)))
    application.add_handler(CommandHandler("guide", admin_only(cmd_guide)))
    application.add_handler(CommandHandler("menu", admin_only(cmd_menu)))

    # 汉字命令：所有群友可用
    application.add_handler(MessageHandler(filters.Regex(r'^\s*资料帮助\s*$'), cmd_help))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*我的资料\s*$'), cmd_profile))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*我的活动\s*$'), cmd_activity))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*资料统计\s*$'), cmd_stats))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*我的成就\s*$'), cmd_achievements))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*隐私设置\s*$'), cmd_privacy))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*积分规则\s*$'), cmd_pointsrules))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*导航\s*$'), cmd_guide))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*菜单\s*$'), cmd_menu))

    # 导航里「积分规则」按钮回调
    application.add_handler(CallbackQueryHandler(handle_guide_callback, pattern='^show_points_rules$'))

    # 进群自动弹底部菜单（两种进群方式都覆盖）
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_join_menu))
    application.add_handler(ChatMemberHandler(handle_join_menu_cm, ChatMemberHandler.CHAT_MEMBER))

    # 错误处理
    application.add_error_handler(error_handler)

    # 初始化回调
    application.post_init = post_init

    # 启动
    logger.info("UserBot 启动中...")
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            stop_signals=[2, 15],
            timeout=30,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30
        )
    except KeyboardInterrupt:
        logger.info("UserBot 被中断")
    except Exception as e:
        logger.error(f"UserBot 运行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
