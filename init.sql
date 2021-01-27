CREATE DATABASE IF NOT EXISTS telegram_uploader;
GRANT ALL PRIVILEGES ON telegram_uploader.* TO 'telegram_user'@'%';
FLUSH PRIVILEGES;
