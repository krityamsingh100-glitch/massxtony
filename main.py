import asyncio
import logging
from pyrogram import Client
from core.bot import ReportBot
from config.settings import Config
from utils.logger import setup_logging

# 设置日志
setup_logging()

logger = logging.getLogger(__name__)

async def main():
    """主程序入口"""
    logger.info("Starting Telegram Report Manager...")
    
    try:
        # 初始化机器人
        bot = ReportBot(
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="handlers")
        )
        
        # 启动机器人
        await bot.start()
        logger.info(f"Bot started successfully as @{(await bot.get_me()).username}")
        
        # 保持运行
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        if 'bot' in locals():
            await bot.stop()
            logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
