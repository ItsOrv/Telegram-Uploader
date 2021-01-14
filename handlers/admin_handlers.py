from datetime import datetime
from telethon import events, Button
from config.logger_config import logger
from utils.keyboards import Keyboards

class AdminHandlers:
    def __init__(self, bot, config, db):
        self.bot = bot
        self.config = config
        self.db = db
        self.keyboards = Keyboards(config)

    async def handle_start_admin(self, event):
        user_id = event.sender_id
        logger.info(f"Admin panel accessed by {user_id}")
        await event.respond(
            "پنل مدیریت",
            buttons=self.keyboards.get_admin_panel_buttons()
        )

    async def handle_admin_commands(self, event):
        command = event.data.decode('utf-8')
        user_id = event.sender_id
        logger.info(f"Admin command: {command} from {user_id}")

        if command == "upload_file_admin":
            await self.upload_file_admin(event)
        elif command == "delete_file_admin":
            await self.delete_file_admin(event)
        elif command == "back_to_admin_panel":
            await event.edit("پنل مدیریت", buttons=self.keyboards.get_admin_panel_buttons())

    async def upload_file_admin(self, event):
        admin_id = event.sender_id
        if not self.db.is_admin(admin_id):
            await event.edit("شما دسترسی ندارید.")
            return

        admin_info = self.db.get_admin(admin_id)
        if not admin_info or not admin_info.get('group_id') or not admin_info.get('group_backup_id'):
            await event.edit("ابتدا گروه اصلی و بکاپ را ست کنید.")
            return

        await event.edit("فایل را ارسال کنید:")

    async def delete_file_admin(self, event):
        await event.edit("هش فایل را ارسال کنید:")

    async def add_required_channel(self, event):
        await event.edit("یوزرنیم کانال را ارسال کنید:")

    async def set_main_group(self, event):
        group_id = event.chat_id
        admin_id = event.sender_id
        self.db.update_admin_group(admin_id, group_id=group_id)
        await event.respond("گروه اصلی ست شد.")

    async def set_backup_group(self, event):
        group_id = event.chat_id
        admin_id = event.sender_id
        self.db.update_admin_group(admin_id, backup_group_id=group_id)
        await event.respond("گروه بکاپ ست شد.")

    async def cancel(self, event):
        await event.edit("لغو شد.", buttons=self.keyboards.get_admin_panel_buttons())
