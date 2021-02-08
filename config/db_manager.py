import mysql.connector
from mysql.connector import Error
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabaseManager:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config=None):
        if self._initialized:
            return
        if config is None:
            raise ValueError("Config required for first init")
        self.config = config
        self.connection = None
        self.connect()
        self._initialized = True

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.config.mysql_host,
            port=self.config.mysql_port,
            user=self.config.mysql_user,
            password=self.config.mysql_password,
            database=self.config.mysql_database,
            autocommit=True
        )

    def reconnect(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def execute_query(self, query, params=None):
        try:
            if not self.connection.is_connected():
                self.reconnect()
            with self.connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                self.connection.commit()
                return None
        except Error as e:
            print(f"DB error: {e}")
            raise

    def add_user(self, user_id, has_access=False):
        self.execute_query("INSERT IGNORE INTO users (user_id, has_access) VALUES (%s, %s)",
                          (user_id, has_access))

    def get_user(self, user_id):
        result = self.execute_query("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return result[0] if result else None

    def update_user_access(self, user_id, has_access):
        self.execute_query("UPDATE users SET has_access = %s WHERE user_id = %s",
                          (has_access, user_id))

    def is_admin(self, user_id):
        result = self.execute_query("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        return bool(result)

    def add_admin(self, user_id, group_id=None, group_backup_id=None):
        if self.is_admin(user_id):
            raise ValueError("already an admin")
        self.execute_query("INSERT INTO admins (user_id, group_id, group_backup_id) VALUES (%s, %s, %s)",
                          (user_id, group_id, group_backup_id))

    def get_admin(self, user_id):
        result = self.execute_query("SELECT * FROM admins WHERE user_id = %s", (user_id,))
        return result[0] if result else None

    def remove_admin(self, user_id):
        if not self.is_admin(user_id):
            raise ValueError("not an admin")
        self.execute_query("DELETE FROM admins WHERE user_id = %s", (user_id,))

    def get_all_admins(self):
        return self.execute_query("SELECT * FROM admins ORDER BY id DESC") or []

    def get_all_users(self):
        return self.execute_query("SELECT * FROM users") or []

    def is_banned(self, user_id):
        result = self.execute_query("SELECT 1 FROM banned_users WHERE user_id = %s", (user_id,))
        return bool(result)

    def ban_user(self, user_id, reason=None):
        if not self.get_user(user_id):
            raise ValueError("user not found")
        if self.is_banned(user_id):
            raise ValueError("already banned")
        self.execute_query("INSERT INTO banned_users (user_id, ban_reason) VALUES (%s, %s)",
                          (user_id, reason))

    def unban_user(self, user_id):
        try:
            if not self.is_banned(user_id):
                raise ValueError("این کاربر در لیست سیاه نیست")
            self.execute_query("DELETE FROM banned_users WHERE user_id = %s", (user_id,))
        except Exception as e:
            from config.logger_config import logger
            logger.error(f"Error in unban_user: {e}", exc_info=True)
            raise

    def add_file(self, file_id, user_id, file_name, file_size, mime_type, uploader_id, caption=None):
        self.execute_query("""INSERT INTO files (file_id, user_id, file_name, file_size, mime_type, uploader_id, caption)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                          (file_id, user_id, file_name, file_size, mime_type, uploader_id, caption))

    def get_file(self, file_id):
        result = self.execute_query("SELECT * FROM files WHERE file_id = %s", (file_id,))
        return result[0] if result else None

    def get_file_by_hash(self, file_hash):
        result = self.execute_query("SELECT * FROM files WHERE hash_file = %s", (file_hash,))
        return result[0] if result else None

    def add_file_download(self, user_id, file_id):
        self.execute_query("INSERT INTO downloaded_files (user_id, file_id) VALUES (%s, %s)",
                          (user_id, file_id))

    def add_required_channel(self, channel_id, channel_username, channel_title, added_by):
        self.execute_query("""INSERT INTO required_channels (channel_id, channel_username, channel_title, added_by)
                              VALUES (%s, %s, %s, %s)""",
                          (channel_id, channel_username, channel_title, added_by))

    def get_required_channels(self):
        return self.execute_query("SELECT * FROM required_channels WHERE is_active = TRUE") or []

    def update_admin_group(self, admin_id, group_id=None, backup_group_id=None):
        if group_id is not None:
            self.execute_query("UPDATE admins SET group_id = %s WHERE user_id = %s", (group_id, admin_id))
        if backup_group_id is not None:
            self.execute_query("UPDATE admins SET group_backup_id = %s WHERE user_id = %s", (backup_group_id, admin_id))

    def log_user_activity(self, user_id, activity_type, details):
        try:
            self.execute_query("""INSERT INTO user_activity_log (user_id, activity_type, details)
                                  VALUES (%s, %s, %s)""",
                              (user_id, activity_type, details))
        except Exception:
            pass

    def get_system_stats(self):
        result = self.execute_query("""SELECT
            (SELECT COUNT(*) FROM users) as total_users,
            (SELECT COUNT(*) FROM files) as total_files,
            (SELECT COUNT(*) FROM admins) as total_admins""")
        return result[0] if result else None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
