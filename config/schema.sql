DROP DATABASE IF EXISTS telegram_uploader;
CREATE DATABASE telegram_uploader;
USE telegram_uploader;

-- Create tables first without foreign keys
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    group_id BIGINT,
    group_backup_id BIGINT
);

CREATE TABLE IF NOT EXISTS groups_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id BIGINT NOT NULL UNIQUE,
    group_name VARCHAR(255) NOT NULL,
    group_type ENUM('primary', 'backup') NOT NULL
);

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id VARCHAR(255) NOT NULL UNIQUE,
    hash_file VARCHAR(255),
    admin_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    backup_group_id BIGINT NOT NULL,
    file_name VARCHAR(255),
    file_size BIGINT NOT NULL,
    download_link TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_files_admin_id (admin_id),
    INDEX idx_files_group_id (group_id),
    CONSTRAINT files_admin_fk FOREIGN KEY (admin_id) REFERENCES admins(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    has_access BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS downloaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    file_id VARCHAR(255) NOT NULL,
    download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS banned_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    ban_reason TEXT,
    ban_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS required_channels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    channel_id VARCHAR(255) NOT NULL UNIQUE,
    channel_username VARCHAR(255),
    channel_title VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    added_by BIGINT
);
