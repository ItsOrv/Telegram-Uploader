import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabaseManager:
    def __init__(self, db_path='bot.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            has_access INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            group_id INTEGER,
            group_backup_id INTEGER
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            file_name TEXT,
            hash_file TEXT,
            group_id INTEGER,
            admin_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        self.conn.commit()

    def add_user(self, user_id, has_access=False):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (user_id, has_access) VALUES (?, ?)",
                  (user_id, int(has_access)))
        self.conn.commit()

    def get_user(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return {'user_id': row[0], 'has_access': bool(row[1])} if row else None

    def update_user_access(self, user_id, has_access):
        c = self.conn.cursor()
        c.execute("UPDATE users SET has_access = ? WHERE user_id = ?",
                  (int(has_access), user_id))
        self.conn.commit()

    def is_admin(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
        return bool(c.fetchone())

    def add_admin(self, user_id, group_id=None, group_backup_id=None):
        c = self.conn.cursor()
        c.execute("INSERT OR IGNORE INTO admins VALUES (?, ?, ?)",
                  (user_id, group_id, group_backup_id))
        self.conn.commit()

    def get_admin(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return {'user_id': row[0], 'group_id': row[1], 'group_backup_id': row[2]} if row else None

    def get_file(self, file_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM files WHERE file_id = ?", (file_id,))
        row = c.fetchone()
        if row:
            return {'file_id': row[0], 'file_name': row[1], 'hash_file': row[2],
                    'group_id': row[3], 'admin_id': row[4]}
        return None

    def get_file_by_hash(self, file_hash):
        c = self.conn.cursor()
        c.execute("SELECT * FROM files WHERE hash_file = ?", (file_hash,))
        row = c.fetchone()
        if row:
            return {'file_id': row[0], 'file_name': row[1], 'hash_file': row[2],
                    'group_id': row[3], 'admin_id': row[4]}
        return None

    def get_required_channels(self):
        return []
