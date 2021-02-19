from datetime import datetime
import os
from telethon import events, Button
from telethon.tl.types import ChannelParticipantsAdmins
from config.constants import Constants
from utils.keyboards import Keyboards
from utils.bot_utils import BotUtils
from config.db_manager import DatabaseManager
from utils.security import require_roles, UserRole
from utils.save import Save
from config.logger_config import logger

class AdminHandlers:
    def __init__(self, bot, config, db):
        logger.info("Initializing AdminHandlers")
        self.bot = bot
        self.config = config
        self.db = db
        self.keyboards = Keyboards(config)
        self.bot_utils = BotUtils(bot)
        self.save = Save(bot, config, db)  # Add db parameter here
        self.constants = Constants(config)
        logger.debug("AdminHandlers initialized successfully")

    @require_roles(UserRole.ADMIN)
    async def handle_start_admin(self, event):
        user_id = event.sender_id
        logger.info(f"Admin panel accessed by user {user_id}")
        await event.respond(
            self.constants.ADMIN_PANEL_MESSAGE,
            buttons=self.keyboards.get_admin_panel_buttons()
        )
        logger.debug(f"Admin panel displayed for user {user_id}")

    @require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    async def set_main_group(self, event):
        group_id = event.chat_id
        admin_id = event.sender_id
        logger.info(f"Setting main group {group_id} for admin {admin_id}")
        self.bot_utils.save_group(admin_id, group_id, "main")
        await event.respond(Constants.SET_MAIN_GROUP_SUCCESS)
        logger.debug(f"Main group set successfully for admin {admin_id}")

    @require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    async def set_backup_group(self, event):
        group_id = event.chat_id
        admin_id = event.sender_id
        logger.info(f"Setting backup group {group_id} for admin {admin_id}")
        self.bot_utils.save_group(admin_id, group_id, "backup")
        await event.respond(Constants.SET_BACKUP_GROUP_SUCCESS)
        logger.debug(f"Backup group set successfully for admin {admin_id}")

    @require_roles(UserRole.ADMIN)
    async def handle_admin_commands(self, event):
        command = event.data.decode('utf-8')
        user_id = event.sender_id
        logger.info(f"Admin command received: {command} from user {user_id}")

        if command == "upload_file_admin":
            await self.upload_file_admin(event)
        elif command == "delete_file_admin":
            await self.delete_file_admin(event)
        elif command == "back_to_admin_panel":
            await event.edit(
                self.constants.ADMIN_PANEL_MESSAGE,
                buttons=self.keyboards.get_admin_panel_buttons()
            )
        logger.debug(f"Admin command {command} handled for user {user_id}")

    @require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)
    async def upload_file_admin(self, event):
        admin_id = event.sender_id
        logger.info(f"File upload initiated by admin {admin_id}")

        # Check if admin has groups set up
        admin_info = self.db.get_admin(admin_id)

        if not admin_info or not admin_info.get('group_id') or not admin_info.get('group_backup_id'):
            logger.warning(f"Admin {admin_id} attempted upload without configured groups")
            await event.edit(self.constants.SET_GROUP_HELP)
            return

        await event.edit("فایل را ارسال کنید:")

        async def handle_file(file_event):
            if file_event.file:
                try:
                    file_info = await self.save.save_file_to_group(file_event, admin_id)
                    link = f"https://t.me/{self.config.bot_username}?start={file_info['hash_file']}"
                    await file_event.respond(f"فایل ذخیره شد.\nلینک: {link}")
                except Exception as e:
                    logger.error(f"Error saving file: {e}", exc_info=True)
                    await file_event.respond(self.constants.ERROR_MESSAGE)
            self.bot.remove_event_handler(handle_file)

        self.bot.add_event_handler(handle_file, events.NewMessage(
            chats=event.chat_id, incoming=True
        ))

    @require_roles(UserRole.ADMIN)
    async def delete_file_admin(self, event):
        await event.edit("هش فایل را ارسال کنید:")

    async def cancel(self, event):
        await event.edit("لغو شد.", buttons=self.keyboards.get_admin_panel_buttons())

    async def add_required_channel(self, event):
        await event.edit("یوزرنیم کانال را ارسال کنید:")
