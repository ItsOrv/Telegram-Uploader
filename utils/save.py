import hashlib
from config.logger_config import logger

class Save:
    def __init__(self, bot, config, db):
        self.bot = bot
        self.config = config
        self.db = db

    async def save_file_to_group(self, message, user_id):
        try:
            file = message.file
            admin_info = self.db.get_admin(user_id)

            if not admin_info or not admin_info.get('group_id'):
                raise ValueError("group not set")

            group_id = admin_info['group_id']
            sent_message = await self.bot.send_file(group_id, file)

            file_id = str(sent_message.id)
            return {
                'file_id': file_id,
                'group_id': str(group_id),
                'file_name': file.name,
                'file_size': file.size,
                'mime_type': file.mime_type,
                'uploader_id': user_id
            }
        except Exception as e:
            logger.error(f"save_file_to_group error: {e}", exc_info=True)
            raise

    def get_file_info(self, file_hash):
        return self.db.get_file_by_hash(file_hash)
