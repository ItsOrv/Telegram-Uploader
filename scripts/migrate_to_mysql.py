"""Migrate data from SQLite to MySQL."""
import sqlite3
import mysql.connector
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate(sqlite_path, mysql_config):
    print(f"Reading from {sqlite_path}")
    sq = sqlite3.connect(sqlite_path)
    sq.row_factory = sqlite3.Row

    my = mysql.connector.connect(**mysql_config)
    cur = my.cursor()

    rows = sq.execute("SELECT * FROM users").fetchall()
    for r in rows:
        try:
            cur.execute("INSERT IGNORE INTO users (user_id, has_access) VALUES (%s, %s)",
                        (r['user_id'], bool(r['has_access'])))
        except Exception as e:
            print(f"  user {r['user_id']}: {e}")

    rows = sq.execute("SELECT * FROM admins").fetchall()
    for r in rows:
        try:
            cur.execute("INSERT IGNORE INTO admins (user_id, group_id, group_backup_id) VALUES (%s, %s, %s)",
                        (r['user_id'], r['group_id'], r['group_backup_id']))
        except Exception as e:
            print(f"  admin {r['user_id']}: {e}")

    my.commit()
    print("Migration done")
    sq.close()
    my.close()

if __name__ == '__main__':
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlite', default='bot.db')
    args = parser.parse_args()

    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE', 'telegram_uploader')
    }
    migrate(args.sqlite, config)
