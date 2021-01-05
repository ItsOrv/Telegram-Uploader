CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    has_access INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    group_id INTEGER,
    group_backup_id INTEGER
);

CREATE TABLE IF NOT EXISTS files (
    file_id TEXT PRIMARY KEY,
    file_name TEXT,
    hash_file TEXT,
    group_id INTEGER,
    admin_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    file_id TEXT,
    download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS banned_users (
    user_id INTEGER PRIMARY KEY,
    ban_reason TEXT,
    ban_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
