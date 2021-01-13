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

    async def check_user_membership(self, user_id):
        channels = self.db.get_required_channels()
        for ch in channels:
            if not await self.is_user_member(user_id, ch['channel_id']):
                return False
        return True

    async def is_user_member(self, user_id, channel_id):
        try:
            from telethon.tl.types import ChannelParticipant
            participant = await self.bot(GetParticipantRequest(channel_id, user_id))
            return isinstance(participant.participant, ChannelParticipant)
        except Exception:
            return False

    async def handle_user_commands(self, event):
        command = event.data.decode('utf-8')
        user_id = event.sender_id

        if command == "request_upload_file":
            await self.request_upload_file_user(event)
        elif command == "support":
            await self.support_user(event)
        elif command.startswith("check_membership:"):
            file_hash = command.split(":")[1]
            await self.check_membership_and_send_file(event, file_hash)
        elif command == "cancel":
            await self.cancel(event)

    async def check_membership_and_send_file(self, event, file_hash):
        user_id = event.sender_id
        if await self.check_user_membership(user_id):
            await self.forward_message(file_hash, user_id)
        else:
            await event.respond("هنوز عضو کانال نشدی")

    async def forward_message(self, file_hash, user_id):
        import asyncio
        file_info = self.db.get_file_by_hash(file_hash)
        if file_info:
            message = await self.bot.get_messages(file_info['group_id'], ids=int(file_info['file_id']))
            sent = await self.bot.send_message(user_id, message)
            self.db.add_file_download(user_id, file_info['file_id'])
            await asyncio.sleep(self.config.delete_delay)
            await self.bot.delete_messages(user_id, sent)
        else:
            await self.bot.send_message(user_id, "فایل پیدا نشد")

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
