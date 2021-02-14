# Telegram File Uploader Bot

A powerful Telegram bot for managing file uploads in groups with advanced admin controls and file management features.

## Features
- File upload management with size and type restrictions
- Multi-level user management (Super Admin, Admin, Users)
- Group-based file sharing
- Automatic file validation and filtering
- Rate limiting and quota management
- Detailed logging and monitoring

## Prerequisites
- Python 3.8+
- MySQL Server
- Telegram Bot Token (from @BotFather)
- Telegram API credentials (api_id and api_hash)

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Telegram-Uploader.git
cd Telegram-Uploader
```

2. Copy example environment file and configure:
```bash
cp .env.example .env
```
Edit `.env` with your credentials and settings.

3. Setup using Docker (Recommended):
```bash
docker-compose up --build
```

OR Manual Setup:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup database
mysql -u root -p < setup_db.sql

# Run the bot
python main.py
```

## Environment Variables
Configure these in `.env`:
- `API_ID`: Telegram API ID
- `API_HASH`: Telegram API Hash
- `BOT_TOKEN`: Telegram Bot Token
- `SUPER_ADMIN_ID`: Your Telegram User ID
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
- `ALLOWED_FILE_TYPES`: Comma-separated list of allowed file extensions
- `MAX_FILE_SIZE`: Maximum file size in bytes

## Usage
1. Start the bot: `/start`
2. Admin commands:
   - `/users` - List all users
   - `/ban` - Ban a user
   - `/unban` - Unban a user
   - `/stats` - View statistics
3. Upload files by sending them to the bot
4. Use inline buttons for file management

## Maintenance
- Logs are stored in `logs/bot.log`
- Database backups recommended daily
- Monitor disk usage for uploaded files

## Security Notes
- Keep your API credentials secure
- Regularly update the allowed file types
- Monitor user activity for abuse
- Backup important data regularly

## License
MIT License - See LICENSE file for details
