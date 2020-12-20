import asyncio
from telethon import events, Button
from telethon.tl.types import Channel
from config.constants import Constants
from utils.keyboards import Keyboards
from config.db_manager import DatabaseManager
from utils.security import check_user_access, UserRole
from config.logger_config import logger

class StartHandlers:
    def __init__(self, bot, config, db):
        logger.info("Initializing StartHandlers")
        self.bot = bot
        self.config = config
        self.db = db
        self.keyboards = Keyboards(config)
        self.constants = Constants(config)
        logger.debug("StartHandlers initialized successfully")

    async def handle_start(self, event):
        user_id = event.sender_id
        logger.info(f"Start command received from user {user_id}")

        try:
            user = self.db.get_user(user_id)
            if not user:
                logger.info(f"New user {user_id} registered")
                self.db.add_user(user_id)

            start_param = event.message.message.split(' ')[1] if len(event.message.message.split(' ')) > 1 else None

            if start_param:
                logger.info(f"Start parameter received: {start_param}")
                return await self._handle_file_download(event, start_param)

            access_level = await check_user_access(self.db, user_id)
            logger.debug(f"User {user_id} access level: {access_level}")

            if access_level == UserRole.SUPER_ADMIN:
                await self._handle_super_admin_start(event)
            elif access_level == UserRole.ADMIN:
                await self._handle_admin_start(event)
            else:
                await self._handle_user_start(event)

        except Exception as e:
            logger.error(f"Error handling start command for user {user_id}: {e}", exc_info=True)
            await event.respond(self.constants.user.ERROR)

    async def _handle_super_admin_start(self, event):
        try:
            logger.debug("Displaying super admin panel")
            await event.respond(
                self.constants.super_admin.WELCOME,
                buttons=self.keyboards.get_super_admin_panel_buttons()
            )
        except Exception as e:
            logger.error(f"Error in super admin start: {e}", exc_info=True)
            raise

    async def _handle_admin_start(self, event):
        try:
            logger.debug("Displaying admin panel")
            await event.respond(
                self.constants.ADMIN_PANEL_MESSAGE,
                buttons=self.keyboards.get_admin_panel_buttons()
            )
        except Exception as e:
            logger.error(f"Error in admin start: {e}", exc_info=True)
            raise

    async def _handle_user_start(self, event):
        try:
            logger.debug("Displaying user panel")
            await event.respond(
                self.constants.WELCOME_MESSAGE,
                buttons=self.keyboards.get_user_buttons()
            )
        except Exception as e:
            logger.error(f"Error in user start: {e}", exc_info=True)
            raise

    async def _handle_file_download(self, event, file_hash):
        user_id = event.sender_id
        logger.info(f"File download request: {file_hash} from user {user_id}")
        try:
            channels = self.db.get_required_channels()
            for ch in channels:
                try:
                    participant = await self.bot(
                        __import__('telethon').tl.functions.channels.GetParticipantRequest(
                            ch['channel_id'], user_id
                        )
                    )
                except Exception:
                    await event.respond(
                        self.constants.MANDATORY_JOIN_MESSAGE,
                        buttons=await self._get_channel_buttons(file_hash)
                    )
                    return

            file_info = self.db.get_file_by_hash(file_hash)
            if file_info:
                message = await self.bot.get_messages(file_info['group_id'], ids=int(file_info['file_id']))
                sent = await self.bot.send_message(user_id, message)
                self.db.add_file_download(user_id, file_info['file_id'])
                await asyncio.sleep(self.config.delete_delay)
                await self.bot.delete_messages(user_id, sent)
            else:
                await event.respond(self.constants.file.NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in file download: {e}", exc_info=True)
            await event.respond(self.constants.user.ERROR)

    async def _get_channel_buttons(self, file_hash):
        buttons = []
        channels = self.db.get_required_channels()
        for ch in channels:
            buttons.append([Button.url(ch['channel_title'], f"https://t.me/{ch['channel_username']}")])
        buttons.append([Button.inline("عضو شدم", data=f"check_subscription:{file_hash}")])
        return buttons

    async def handle_set_main(self, event):
        admin_id = event.sender_id
        group_id = event.chat_id
        logger.info(f"Setting main group {group_id} for admin {admin_id}")
        self.db.update_admin_group(admin_id, group_id=group_id)
        await event.respond("گروه اصلی ست شد")

    async def handle_set_backup(self, event):
        admin_id = event.sender_id
        group_id = event.chat_id
        logger.info(f"Setting backup group {group_id} for admin {admin_id}")
        self.db.update_admin_group(admin_id, backup_group_id=group_id)
        await event.respond("گروه بکاپ ست شد")

    async def check_subscription_callback(self, event):
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        file_hash = data.split(':')[1] if ':' in data else None
        logger.info(f"Subscription check for user {user_id}, file: {file_hash}")

        channels = self.db.get_required_channels()
        for ch in channels:
            try:
                await self.bot(
                    __import__('telethon').tl.functions.channels.GetParticipantRequest(
                        ch['channel_id'], user_id
                    )
                )
            except Exception:
                await event.answer("هنوز عضو نشدی", alert=True)
                return

        if file_hash:
            await self._handle_file_download(event, file_hash)
        else:
            await event.answer("عضویت تایید شد", alert=True)
