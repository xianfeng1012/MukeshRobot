"""
MiniAppBot 主程序
小程序管理机器人 - 负责积分系统、任务、Mini App集成
"""
import logging
import sys
from datetime import time as dt_time, timezone, timedelta
from functools import partial
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import MINIAPP_BOT_TOKEN, LOG_LEVEL, LOG_FILE, PUBLISH_SECRET, PUBLISH_WEBHOOK_PORT
from handlers import (
    cmd_points, cmd_leaderboard, cmd_play, cmd_checkin, cmd_tasks, cmd_stats,
    cmd_schedule, publish_schedule_to_channel, send_girl_teaser,
    publish_profile_to_channel, publish_review, admin_only, text_checkin
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
    """开始命令（带 girl_<id> 参数时推送该人物资料）"""
    args = context.args
    if args and args[0].startswith('girl_'):
        girl_id = args[0][len('girl_'):]
        await send_girl_teaser(update, context, girl_id)
        return

    await update.message.reply_text(
        "🎮 *小程序管理机器人*\n\n"
        "欢迎使用！我负责:\n"
        "💰 积分系统\n"
        "🎯 任务管理\n"
        "🏆 排行榜\n"
        "🎮 Mini App集成\n\n"
        "*可用命令:*\n"
        "/play - 打开小程序\n"
        "/points - 查看积分\n"
        "/leaderboard - 查看排行榜\n"
        "/checkin - 每日签到\n"
        "/tasks - 任务列表\n"
        "/stats - 个人统计\n"
        "/schedule - 今日开课老师",
        parse_mode='Markdown'
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助命令"""
    await update.message.reply_text(
        "📖 *小程序机器人帮助*\n\n"
        "*命令列表:*\n"
        "/play - 🎮 打开小程序\n"
        "/points - 💰 查看你的积分和等级\n"
        "/leaderboard - 🏆 查看积分排行榜\n"
        "/checkin - 📅 每日签到\n"
        "/tasks - 📋 查看可用任务\n"
        "/stats - 📊 查看个人统计\n"
        "/schedule - 📋 今日开课老师（汉字「今日开课」）\n"
        "/help - ❓ 显示此帮助信息",
        parse_mode='Markdown'
    )


# ============ 资料发布 Webhook ============
async def _handle_publish(request: web.Request) -> web.Response:
    """接收 yanyulou admin 的发布请求 → 发到对应频道"""
    if request.headers.get('X-Publish-Key') != PUBLISH_SECRET:
        return web.json_response({'success': False, 'message': 'invalid key'}, status=401)
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({'success': False, 'message': 'bad json'}, status=400)

    application: Application = request.app['tg_app']
    # 同步执行并返回 messageIds（供后端记录、下次就地编辑）。发图调用已设较长超时，
    # 单次相册请求不会触发客户端超时。
    try:
        result = await publish_profile_to_channel(application.bot, payload)
        return web.json_response(result, status=200 if result.get('success') else 400)
    except Exception as e:
        logger.error(f"发布处理异常: {e}")
        return web.json_response({'success': False, 'message': str(e)}, status=500)


async def _handle_publish_review(request: web.Request) -> web.Response:
    """接收 yanyulou admin 的优质评价发布请求 → 发到报告频道+群"""
    if request.headers.get('X-Publish-Key') != PUBLISH_SECRET:
        return web.json_response({'success': False, 'message': 'invalid key'}, status=401)
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({'success': False, 'message': 'bad json'}, status=400)

    username = (payload.get('username') or '').strip() or '群友'
    content = (payload.get('content') or '').strip()
    if not content:
        return web.json_response({'success': False, 'message': '评论内容为空'}, status=400)

    application: Application = request.app['tg_app']
    try:
        result = await publish_review(application.bot, username, content)
        return web.json_response(result, status=200 if result.get('success') else 400)
    except Exception as e:
        logger.error(f"优质评价发布异常: {e}")
        return web.json_response({'success': False, 'message': str(e)}, status=500)


# ============ 应用初始化 ============
async def post_init(application: Application) -> None:
    """应用初始化后的回调：启动发布 Webhook 服务"""
    web_app = web.Application()
    web_app['tg_app'] = application
    web_app.router.add_post('/publish-profile', _handle_publish)
    web_app.router.add_post('/publish-review', _handle_publish_review)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PUBLISH_WEBHOOK_PORT)
    await site.start()
    application.bot_data['_web_runner'] = runner
    logger.info(f"MiniAppBot 已启动；发布 Webhook 监听 :{PUBLISH_WEBHOOK_PORT}/publish-profile")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """错误处理"""
    logger.error(f"MiniAppBot 发生错误: {context.error}", exc_info=context.error)


def main():
    """主函数"""
    # 检查Token
    if not MINIAPP_BOT_TOKEN:
        logger.error("MINIAPP_BOT_TOKEN 未设置")
        sys.exit(1)

    # 创建应用
    application = Application.builder().token(MINIAPP_BOT_TOKEN).build()

    # 注册处理器
    # 斜杠命令：群内仅管理员有效（私聊不限制；/start 私聊还承担 girl_ 深链接）。
    # 普通群友在群里请用汉字命令。
    application.add_handler(CommandHandler("start", admin_only(cmd_start)))
    application.add_handler(CommandHandler("help", admin_only(cmd_help)))
    application.add_handler(CommandHandler("play", admin_only(cmd_play)))
    application.add_handler(CommandHandler("points", admin_only(cmd_points)))
    application.add_handler(CommandHandler("leaderboard", admin_only(cmd_leaderboard)))
    application.add_handler(CommandHandler("checkin", admin_only(cmd_checkin)))
    application.add_handler(CommandHandler("tasks", admin_only(cmd_tasks)))
    application.add_handler(CommandHandler("stats", admin_only(cmd_stats)))
    application.add_handler(CommandHandler("schedule", admin_only(cmd_schedule)))

    # 汉字命令：所有群友可用，均保留成员发言（不自动删除）。
    application.add_handler(MessageHandler(filters.Regex(r'^\s*签到\s*$'), text_checkin))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*积分\s*$'), partial(cmd_points, clean=False)))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*排行榜\s*$'), partial(cmd_leaderboard, clean=False)))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*任务\s*$'), partial(cmd_tasks, clean=False)))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*我的统计\s*$'), partial(cmd_stats, clean=False)))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*小程序\s*$'), cmd_play))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*今日开课\s*$'), partial(cmd_schedule, clean=False)))
    application.add_handler(MessageHandler(filters.Regex(r'^\s*玩法帮助\s*$'), cmd_help))

    # 每日 14:00（北京时间）自动把「今日开课」发布到公示榜频道
    application.job_queue.run_daily(
        publish_schedule_to_channel,
        time=dt_time(14, 0, tzinfo=timezone(timedelta(hours=8))),
        name='daily_schedule_publish',
    )

    # 错误处理
    application.add_error_handler(error_handler)

    # 初始化回调
    application.post_init = post_init

    # 启动
    logger.info("MiniAppBot 启动中...")
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
        logger.info("MiniAppBot 被中断")
    except Exception as e:
        logger.error(f"MiniAppBot 运行失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
