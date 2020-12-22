from config.logger_config import logger

class Send:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    def get_file_info(self, file_hash):
        return None

    async def send_file(self, user_id, file_info):
        try:
            await self.bot.send_file(user_id, file_info)
        except Exception as e:
            logger.error(f"send_file error: {e}", exc_info=True)
            raise
