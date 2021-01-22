from telethon import TelegramClient
from config.config import Config
from handlers.admin_handlers import AdminHandlers
from handlers.super_admin_handlers import SuperAdminHandlers
from handlers.user_handlers import UserStart
from handlers.start_handlers import StartHandlers
from utils.keyboards import Keyboards
from utils.save import Save
from utils.send import Send
from config.db_manager import DatabaseManager
from config.logger_config import logger
import asyncio

async def main():
    config = Config()
    bot = TelegramClient('bot_session', config.api_id, config.api_hash)
    await bot.start(bot_token=config.bot_token)

    db = DatabaseManager(config)

    admin_handlers = AdminHandlers(bot, config, db)
    super_admin_handlers = SuperAdminHandlers(bot, config, admin_handlers, db)
    user_start = UserStart(bot, config, db)
    start_handlers = StartHandlers(bot, config, db)

    from telethon import events
    bot.add_event_handler(start_handlers.handle_start, events.NewMessage(pattern='/start'))

    logger.info("Bot started")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
