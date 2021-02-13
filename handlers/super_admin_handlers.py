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
        elif command == "ban_user":
            await self.ban_user_prompt(event)
        elif command == "unban_user":
            await self.unban_user_prompt(event)
        elif command == "get_database_file":
            await self.get_database_file(event)

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

    async def ban_user_prompt(self, event):
        await event.edit("آیدی کاربر را برای بن کردن ارسال کنید:",
                         buttons=[Button.inline("انصراف", b"cancel_ban_user")])
        self.bot.add_event_handler(self._handle_ban_input, __import__('telethon').events.NewMessage(
            from_users=event.sender_id, incoming=True))

    async def _handle_ban_input(self, event):
        self.bot.remove_event_handler(self._handle_ban_input)
        try:
            user_id = int(event.text)
            self.db.ban_user(user_id)
            await event.respond(f"کاربر {user_id} بن شد.")
        except ValueError:
            await event.respond("آیدی معتبر نیست.")
        except Exception as e:
            await event.respond(f"خطا: {e}")

    async def unban_user_prompt(self, event):
        await event.edit("آیدی کاربر را برای رفع بن ارسال کنید:",
                         buttons=[Button.inline("انصراف", b"cancel_unban_user")])

    async def get_database_file(self, event):
        user_id = event.sender_id
        try:
            backup_path = self.db.export_database()
            await self.bot.send_file(user_id, backup_path, caption="database backup")
            import os
            os.remove(backup_path)
        except Exception as e:
            logger.error(f"Backup error: {e}", exc_info=True)
            await event.respond(f"خطا در تهیه بکاپ: {e}")
