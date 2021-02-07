from config.db_manager import DatabaseManager
from config.logger_config import logger

class BotUtils:
    def __init__(self, bot):
        logger.info("Initializing BotUtils")
        self.bot = bot
        self.db = None
        logger.debug("BotUtils instance created")

    def init_db(self, config):
        try:
            logger.info("Initializing database connection for BotUtils")
            self.db = DatabaseManager(config)
            logger.debug("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    def is_admin(self, user_id):
        try:
            return bool(self.db.get_admin(user_id))
        except Exception as e:
            logger.error(f"Error checking admin status for {user_id}: {e}", exc_info=True)
            return False

    def get_group_id(self, admin_id, group_type):
        try:
            admin_info = self.db.get_admin(admin_id)
            if admin_info:
                if group_type == "primary":
                    return admin_info['group_id']
                elif group_type == "backup":
                    return admin_info['group_backup_id']
            return None
        except Exception as e:
            logger.error(f"Error getting group ID for {admin_id}: {e}", exc_info=True)
            return None

    def save_group(self, admin_id, group_id, group_type):
        try:
            if not self.db:
                raise RuntimeError("Database not initialized")
            if group_type == "main":
                self.db.update_admin_group(admin_id, group_id=group_id)
            else:
                self.db.update_admin_group(admin_id, backup_group_id=group_id)
        except Exception as e:
            logger.error(f"Error saving group for {admin_id}: {e}", exc_info=True)
            raise

    def save_banned_user(self, user_id):
        try:
            if self.db is None:
                raise RuntimeError("Database not initialized")
            if self.db.is_banned(user_id):
                raise ValueError("already banned")
            self.db.ban_user(user_id)
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}", exc_info=True)
            raise

    def remove_banned_user(self, user_id):
        try:
            if self.db is None:
                raise RuntimeError("Database not initialized")
            if not self.db.is_banned(user_id):
                raise ValueError("not banned")
            self.db.unban_user(user_id)
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}", exc_info=True)
            raise

    def check_admin_groups(self, admin_id):
        try:
            if not self.db:
                return False
            admin = self.db.get_admin(admin_id)
            return bool(admin and admin.get('group_id') and admin.get('group_backup_id'))
        except Exception as e:
            logger.error(f"Error checking admin groups for {admin_id}: {e}", exc_info=True)
            return False
