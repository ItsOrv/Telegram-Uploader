import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self._api_id = int(os.getenv('API_ID'))
        self._api_hash = os.getenv('API_HASH')
        self._bot_token = os.getenv('BOT_TOKEN')

    @property
    def api_id(self):
        return self._api_id

    @property
    def api_hash(self):
        return self._api_hash

    @property
    def bot_token(self):
        return self._bot_token
