from telethon import events, Button
from config.logger_config import logger
from utils.keyboards import Keyboards

class SuperAdminHandlers:
    def __init__(self, bot, config, admin_handlers, db):
        self.bot = bot
        self.config = config
        self.admin_handlers = admin_handlers
        self.db = db
        self.keyboards = Keyboards(config)

    async def handle_super_admin_commands(self, event):
        command = event.data.decode('utf-8')
        user_id = event.sender_id
        logger.info(f"Super admin command: {command} from {user_id}")

        if user_id != self.config.super_admin_id:
            return

        if command == "back_to_super_admin_panel":
            await event.edit("پنل سوپر ادمین", buttons=self.keyboards.get_super_admin_panel_buttons())
        elif command == "manage_admins":
            await self.manage_admins(event)
        elif command == "manage_users":
            await self.manage_users(event)
        elif command == "add_admin":
            await self.add_admin(event)
        elif command == "remove_admin":
            await self.remove_admin(event)

    async def manage_admins(self, event):
        admins = self.db.get_all_admins() or []
        text = f"تعداد ادمین ها: {len(admins)}"
        buttons = [
            [Button.inline("اضافه کردن ادمین", b"add_admin")],
            [Button.inline("حذف ادمین", b"remove_admin")],
            [Button.inline("برگشت", b"back_to_super_admin_panel")]
        ]
        await event.edit(text, buttons=buttons)

    async def manage_users(self, event):
        users = self.db.get_all_users() or []
        text = f"تعداد کاربران: {len(users)}"
        buttons = [
            [Button.inline("بن کردن کاربر", b"ban_user")],
            [Button.inline("برگشت", b"back_to_super_admin_panel")]
        ]
        await event.edit(text, buttons=buttons)

    async def add_admin(self, event):
        await event.edit("آیدی کاربر را ارسال کنید:",
                         buttons=[Button.inline("انصراف", b"cancel_add_admin")])

    async def remove_admin(self, event):
        await event.edit("آیدی ادمین را ارسال کنید:",
                         buttons=[Button.inline("انصراف", b"cancel_remove_admin")])
