"""Check if migration from sqlite to mysql is needed."""
import os
import sys

def check():
    db_file = 'bot.db'
    if os.path.exists(db_file):
        print(f"Found sqlite db: {db_file}")
        print("Run migrate_to_mysql.py to migrate")
        return True
    return False

if __name__ == '__main__':
    check()
