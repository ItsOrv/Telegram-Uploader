from telethon import TelegramClient
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def main():
    bot = TelegramClient(
        'bot_session',
        int(os.getenv('API_ID')),
        os.getenv('API_HASH')
    )
    await bot.start(bot_token=os.getenv('BOT_TOKEN'))
    print("bot started")
    await bot.run_until_disconnected()

asyncio.run(main())
