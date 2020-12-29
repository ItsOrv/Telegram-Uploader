from telethon import events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from config.logger_config import logger
from utils.keyboards import Keyboards

class UserStart:
    def __init__(self, bot, config, db):
        self.bot = bot
        self.config = config
        self.db = db
        self.keyboards = Keyboards(config)

    async def handle_start_user(self, event):
        user_id = event.sender_id
        user = self.db.get_user(user_id)
        if not user:
            self.db.add_user(user_id)

        await event.respond(
            "سلام! به ربات خوش آمدید.",
            buttons=self.keyboards.get_user_buttons()
        )

    async def handle_user_commands(self, event):
        command = event.data.decode('utf-8')
        user_id = event.sender_id

        if command == "request_upload_file":
            await self.request_upload_file_user(event)
        elif command == "support":
            await self.support_user(event)

    async def request_upload_file_user(self, event):
        user = await event.get_sender()
        user_id = user.id
        username = user.username or "بدون نام"

        await self.bot.send_message(
            self.config.super_admin_id,
            f"درخواست آپلود از کاربر {user_id} (@{username})"
        )
        await event.respond("درخواست ارسال شد.")

    async def support_user(self, event):
        await event.respond(
            "پیام خود را بفرستید:",
            buttons=[Button.inline("انصراف", b"cancel")]
        )

    async def cancel(self, event):
        await event.edit(
            "لغو شد.",
            buttons=self.keyboards.get_user_buttons()
        )
