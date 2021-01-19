import os
from typing import Optional
from dotenv import load_dotenv
from .logger_config import logger

class Config:
    def __init__(self):
        load_dotenv()
        self._api_id = int(os.getenv('API_ID'))
        self._api_hash = os.getenv('API_HASH')
        self._bot_token = os.getenv('BOT_TOKEN')
        self._super_admin_id = int(os.getenv('SUPER_ADMIN_ID'))
        self._delete_delay = int(os.getenv('DELETE_DELAY', 30))
        self._db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'telegram'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE', 'telegram_uploader')
        }
        self._session_file = os.getenv('SESSION_FILE', 'bot_session')
        self._log_file = os.getenv('LOG_FILE', 'logs/bot.log')
        self._max_file_size = int(os.getenv('MAX_FILE_SIZE', 52428800))
        self._allowed_file_types = os.getenv('ALLOWED_FILE_TYPES', '').split(',')
        self._required_channels = os.getenv('REQUIRED_CHANNELS', '').split(',')
        self._log_level = os.getenv('LOG_LEVEL', 'INFO')

    def validate_config(self):
        required = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'SUPER_ADMIN_ID']
        for var in required:
            if not os.getenv(var):
                raise ValueError(f"Missing required env var: {var}")

    @property
    def api_id(self):
        return self._api_id

    @property
    def api_hash(self):
        return self._api_hash

    @property
    def bot_token(self):
        return self._bot_token

    @property
    def super_admin_id(self):
        return self._super_admin_id

    @property
    def delete_delay(self):
        return self._delete_delay

    @property
    def mysql_host(self):
        return self._db_config['host']

    @property
    def mysql_port(self):
        return self._db_config['port']

    @property
    def mysql_user(self):
        return self._db_config['user']

    @property
    def mysql_password(self):
        return self._db_config['password']

    @property
    def mysql_database(self):
        return self._db_config['database']

    @property
    def session_file(self):
        return self._session_file

    @property
    def log_file(self):
        return self._log_file

    @property
    def max_file_size(self):
        return self._max_file_size

    @property
    def allowed_file_types(self):
        return self._allowed_file_types

    @property
    def required_channels(self):
        return self._required_channels

    @property
    def log_level(self):
        return self._log_level

    @property
    def bot_username(self):
        return getattr(self, '_bot_username', None)

    @bot_username.setter
    def bot_username(self, value):
        self._bot_username = value
