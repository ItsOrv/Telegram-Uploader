import json
import hashlib
from config.db_manager import DatabaseManager
from config.logger_config import logger

class Save:
    def __init__(self, bot, config, db):
        logger.info("Initializing Save utility")
        self.bot = bot
        self.config = config
        self.db = db
        logger.debug("Save utility initialized successfully")

    async def save_file_to_group(self, message, user_id):
        """Save file to group and database."""
        try:
            file = message.file
            admin_info = self.db.get_admin(user_id)

            if not admin_info or not admin_info.get('group_id'):
                raise ValueError("گروه مورد نظر یافت نشد. لطفا ابتدا گروه را تنظیم کنید.")

            group_id = admin_info['group_id']
            backup_group_id = admin_info.get('group_backup_id')

            # Send file to primary group
            sent_message = await self.bot.send_file(group_id, file)

            # Send to backup group if configured
            if backup_group_id:
                await self.bot.send_file(backup_group_id, file)

            raw = f"{sent_message.id}{group_id}{user_id}"
            hash_file = hashlib.md5(raw.encode()).hexdigest()
            download_link = f"https://t.me/{self.config.bot_username}?start={hash_file}"

            file_info = {
                'file_id': str(sent_message.id),
                'hash_file': hash_file,
                'group_id': str(group_id),
                'file_name': file.name,
                'file_size': file.size,
                'mime_type': file.mime_type,
                'uploader_id': user_id,
                'download_link': download_link
            }

            self.db.add_file(
                file_id=file_info['file_id'],
                hash_file=hash_file,
                admin_id=user_id,
                group_id=group_id,
                backup_group_id=backup_group_id,
                file_name=file_info['file_name'],
                file_size=file_info['file_size'],
                download_link=download_link
            )

            logger.info(f"File saved successfully: {hash_file}")
            return file_info

        except Exception as e:
            logger.error(f"Error saving file: {e}", exc_info=True)
            raise

    def get_file_info(self, file_hash):
        return self.db.get_file_by_hash(file_hash)
