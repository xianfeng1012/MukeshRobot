"""
DualBot 主程序
单进程并发跑 N 个对外机器人（每个一个 token），全部共用一个客服群做双向中转。
"""
import asyncio
import logging
import signal
import sys

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import DUAL_BOT_TOKENS, SUPPORT_GROUP_ID, LOG_LEVEL
from handlers import on_customer_message, on_group_reply, cmd_id

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def build_app(token: str, label: str, primary: bool) -> Application:
    """为单个 token 构建一个 Application 并注册处理器。"""
    app = Application.builder().token(token).build()
    app.bot_data['label'] = label
    app.bot_data['primary'] = primary

    # /id：部署辅助，仅主实例响应
    app.add_handler(CommandHandler('id', cmd_id))
    # 客户私聊入站（非系统消息，含命令/媒体一律转发）
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & ~filters.StatusUpdate.ALL,
        on_customer_message,
    ))
    # 客服群内的回复
    app.add_handler(MessageHandler(
        filters.Chat(SUPPORT_GROUP_ID) & filters.REPLY,
        on_group_reply,
    ))
    return app


async def run():
    if not DUAL_BOT_TOKENS:
        logger.error("DUAL_BOT_TOKENS 未设置")
        sys.exit(1)
    if not SUPPORT_GROUP_ID:
        logger.error("SUPPORT_GROUP_ID 未设置")
        sys.exit(1)

    apps = [
        build_app(token, f"Bot{i + 1}", primary=(i == 0))
        for i, token in enumerate(DUAL_BOT_TOKENS)
    ]

    for app in apps:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    logger.info(f"DualBot 已启动 {len(apps)} 个机器人实例，客服群 {SUPPORT_GROUP_ID}")

    # 等待终止信号
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass  # Windows 等平台不支持，靠 KeyboardInterrupt 兜底
    await stop_event.wait()

    logger.info("DualBot 正在关闭...")
    for app in apps:
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except Exception as e:
            logger.error(f"关闭实例失败: {e}")


def main():
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("DualBot 被中断")


if __name__ == '__main__':
    main()
