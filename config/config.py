import os
from typing import Optional
from dotenv import load_dotenv
from .logger_config import logger

class Config:
    """Configuration handler for Telegram Uploader.

    Loads and validates environment variables required for the application.
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        logger.info("Initializing configuration")
        load_dotenv()
        logger.debug("Environment variables loaded from .env file")
        self._api_id = None
        self._api_hash = None
        self._bot_token = None
        self._super_admin_id = None
        self._delete_delay = None
        self._db_config = {}
        self._proxy = {}
        self._session_file = None
        self._log_file = None
        self._max_file_size = None
        self._max_send_count_per_user = None
        self._max_send_count_per_group = None
        self._allowed_file_types = []
        self._required_channels = []
        self._log_level = None
        self.validate_config()
        logger.info("Configuration initialized successfully")

    def validate_config(self) -> None:
        """Validate that all required configuration values are present."""
        required_vars = [
            'API_ID',
            'API_HASH',
            'BOT_TOKEN',
            'SUPER_ADMIN_ID'
        ]

        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Missing required environment variable: {var}")

        # Convert string values to appropriate types
        self._api_id = int(os.getenv('API_ID'))
        self._api_hash = os.getenv('API_HASH')
        self._bot_token = os.getenv('BOT_TOKEN')
        self._super_admin_id = int(os.getenv('SUPER_ADMIN_ID'))

        # Proxy settings for Telegram
        self._proxy = {
            'proxy_type': 'socks5',  # or 'http' depending on your proxy
            'addr': '127.0.0.1',     # your proxy address
            'port': 1080,            # your proxy port
            'username': os.getenv('PROXY_USERNAME', None),
            'password': os.getenv('PROXY_PASSWORD', None)
        }

        # Database configuration
        self._db_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'telegram'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE', 'telegram_uploader')
        }

        # File configuration
        self._session_file = os.getenv('SESSION_FILE', 'bot_session')
        self._log_file = os.getenv('LOG_FILE', 'logs/bot.log')
        self._max_file_size = int(os.getenv('MAX_FILE_SIZE', 52428800))  # 50MB default

        # App configuration
        self._delete_delay = int(os.getenv('DELETE_DELAY', 30))
        self._max_send_count_per_user = int(os.getenv('MAX_SEND_COUNT_PER_USER', 10))
        self._max_send_count_per_group = int(os.getenv('MAX_SEND_COUNT_PER_GROUP', 1000))
        self._allowed_file_types = os.getenv('ALLOWED_FILE_TYPES', '').split(',')
        self._required_channels = os.getenv('REQUIRED_CHANNELS', '').split(',')

        # Logging configuration
        self._log_level = os.getenv('LOG_LEVEL', 'INFO')

    @property
    def api_id(self) -> int:
        return self._api_id

    @property
    def api_hash(self) -> str:
        return self._api_hash

    @property
    def bot_token(self) -> str:
        return self._bot_token

    @property
    def super_admin_id(self) -> int:
        return self._super_admin_id

    @property
    def delete_delay(self) -> int:
        return self._delete_delay

    @property
    def mysql_host(self) -> str:
        return self._db_config['host']

    @property
    def mysql_port(self) -> int:
        return self._db_config['port']

    @property
    def mysql_user(self) -> str:
        return self._db_config['user']

    @property
    def mysql_password(self) -> str:
        return self._db_config['password']

    @property
    def mysql_database(self) -> str:
        return self._db_config['database']

    @property
    def data_file(self) -> str:
        """Remove this property as it's no longer needed"""
        raise NotImplementedError("data_file is deprecated. Use MySQL database instead.")

    @property
    def proxy(self) -> dict:
        return self._proxy

    @property
    def session_file(self) -> str:
        return self._session_file

    @property
    def log_file(self) -> str:
        return self._log_file

    @property
    def max_file_size(self) -> int:
        return self._max_file_size

    @property
    def max_send_count_per_user(self) -> int:
        return self._max_send_count_per_user

    @property
    def max_send_count_per_group(self) -> int:
        return self._max_send_count_per_group

    @property
    def allowed_file_types(self) -> list:
        return self._allowed_file_types

    @property
    def required_channels(self) -> list:
        return self._required_channels

    @property
    def log_level(self) -> str:
        return self._log_level
