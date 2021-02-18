from telethon import TelegramClient
from config.config import Config
from handlers.admin_handlers import AdminHandlers
from handlers.super_admin_handlers import SuperAdminHandlers
from handlers.user_handlers import UserStart
from handlers.start_handlers import StartHandlers
from utils.handler_register import HandlerRegistrar
from utils.keyboards import Keyboards
from utils.save import Save
from utils.send import Send
from utils.bot_utils import BotUtils
from config.db_manager import DatabaseManager  # Add this import
from config.logger_config import logger
import asyncio

async def init_bot(bot, config):
    """Initialize bot and get its information."""
    try:
        bot_info = await bot.get_me()
        if not bot_info.username:
            raise ValueError("unable to get bot username")

        config.bot_username = bot_info.username
        logger.info(f"Bot initialized with username: @{config.bot_username}")
    except Exception as e:
        logger.error(f"Error initializing bot: {str(e)}", exc_info=True)
        raise

async def main():
    try:
        config = Config()

        bot = TelegramClient('bot_session', config.api_id, config.api_hash)
        await bot.start(bot_token=config.bot_token)

        # Initialize database - single instance
        db = DatabaseManager(config)

        # Pass db to Save initialization
        save = Save(bot, config, db)

        # Initialize bot info
        await init_bot(bot, config)

        # Initialize handlers with shared database instance
        admin_handlers = AdminHandlers(bot, config, db)
        super_admin_handlers = SuperAdminHandlers(bot, config, admin_handlers, db)
        user_start = UserStart(bot, config, db)
        start_handlers = StartHandlers(bot, config, db)

        # Initialize utilities
        keyboards = Keyboards(config)
        send = Send(bot, config)
        bot_utils = BotUtils(bot)
        bot_utils.init_db(config)

        # Register all handlers
        handler_registrar = HandlerRegistrar(bot, admin_handlers, super_admin_handlers, user_start, start_handlers)
        handler_registrar.register_handlers()

        logger.info("Bot started successfully")
        await bot.run_until_disconnected()
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
