from telethon import events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant
from config.constants import Constants
from utils.send import Send
from utils.save import Save
from utils.keyboards import Keyboards
from config.db_manager import DatabaseManager
import asyncio
from utils.security import require_roles, UserRole
from config.logger_config import logger

class UserStart:
    def __init__(self, bot, config, db):
        logger.info("Initializing UserStart")
        self.bot = bot
        self.config = config
        self.db = db
        self.save = Save(bot, config, db)  # Add db parameter here
        self.send = Send(bot, config)
        self.keyboards = Keyboards(config)
        self.constants = Constants(config)
        logger.debug("UserStart initialized successfully")

    @require_roles(UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
    async def handle_start_user(self, event):
        user_id = event.sender_id
        logger.info(f"Start command received from user {user_id}")

        start_param = event.message.message.split(' ')[1] if len(event.message.message.split(' ')) > 1 else None

        if start_param:
            file_hash = start_param
            logger.debug(f"Start parameter received: {file_hash}")

            if await self.check_user_membership(user_id):
                logger.info(f"User {user_id} membership verified, forwarding file {file_hash}")
                await self.forward_message(file_hash, user_id)
            else:
                logger.warning(f"User {user_id} needs to join required channels")
                await event.respond(
                    self.constants.MANDATORY_JOIN_MESSAGE,
                    buttons=await self.get_required_channels_buttons(file_hash)
                )
        else:
            logger.debug(f"Displaying welcome message for user {user_id}")
            await event.respond(
                self.constants.WELCOME_MESSAGE,
                buttons=self.keyboards.get_user_buttons()
            )

    async def check_user_membership(self, user_id):
        logger.debug(f"Checking channel memberships for user {user_id}")
        channels = self.db.get_required_channels()

        for channel in channels:
            if not await self.is_user_member(user_id, channel['channel_id']):
                logger.info(f"User {user_id} is not a member of channel {channel['channel_id']}")
                return False

        logger.debug(f"User {user_id} is member of all required channels")
        return True

    async def is_user_member(self, user_id, channel_id):
        try:
            participant = await self.bot(GetParticipantRequest(channel_id, user_id))
            is_member = isinstance(participant.participant, ChannelParticipant)
            logger.debug(f"Channel {channel_id} membership check for user {user_id}: {is_member}")
            return is_member
        except Exception as e:
            logger.error(f"Channel membership check failed for user {user_id}, channel {channel_id}: {e}", exc_info=True)
            return False

    async def get_required_channels_buttons(self, file_hash):
        logger.debug("Getting required channels buttons")
        buttons = []
        channels = self.db.get_required_channels()

        for channel in channels:
            buttons.append([Button.url(channel['channel_title'], f"https://t.me/{channel['channel_username']}")])

        buttons.append([Button.inline("عضو شدم", data=f"check_membership:{file_hash}")])
        logger.debug(f"Created buttons for {len(channels)} channels")
        return buttons

    async def forward_message(self, file_hash, user_id):
        logger.info(f"Forwarding file {file_hash} to user {user_id}")

        file_info = self.db.get_file_by_hash(file_hash)
        if file_info:
            try:
                message_id = file_info['file_id']
                message = await self.bot.get_messages(file_info['group_id'], ids=message_id)
                sent_message = await self.bot.send_message(user_id, message)

                # Log download
                self.db.add_file_download(user_id, file_info['file_id'])
                self.db.log_user_activity(user_id, 'download', f"Downloaded file: {file_hash}")
                logger.info(f"File {file_hash} forwarded successfully to user {user_id}")

                # Handle auto-delete
                await self.bot.send_message(user_id, f"{self.constants.file.DELETE.PENDING}")
                await asyncio.sleep(self.config.delete_delay)
                await self.bot.delete_messages(user_id, sent_message)
                logger.debug(f"Auto-deleted message for user {user_id}")

            except Exception as e:
                logger.error(f"Error forwarding file {file_hash} to user {user_id}: {e}", exc_info=True)
                await self.bot.send_message(user_id, self.constants.ERROR_MESSAGE)
        else:
            logger.warning(f"File {file_hash} not found for user {user_id}")
            await self.bot.send_message(user_id, self.constants.file.NOT_FOUND)

    @require_roles(UserRole.USER, UserRole.ADMIN, UserRole.SUPER_ADMIN)
    async def handle_user_commands(self, event):
        command = event.data.decode('utf-8')
        user_id = event.sender_id
        logger.info(f"User command received: {command} from user {user_id}")

        try:
            if command == "request_upload_file":
                await self.request_upload_file_user(event)
            elif command == "support":
                await self.support_user(event)
            elif command.startswith("check_membership:"):
                file_hash = command.split(":")[1]
                await self.check_membership_and_send_file(event, file_hash)
            elif command == "cancel":
                await self.cancel(event)

            logger.debug(f"Command {command} handled successfully for user {user_id}")

        except Exception as e:
            logger.error(f"Error handling command {command} for user {user_id}: {e}", exc_info=True)
            await event.respond(self.constants.ERROR_MESSAGE)

    async def check_membership_and_send_file(self, event, file_hash):
        user_id = event.sender_id
        logger.info(f"Checking membership for user {user_id} to send file {file_hash}")

        if await self._check_channel_subscription(event):  # اینجا تغییر کرد
            logger.info(f"Membership verified for user {user_id}, proceeding with file forward")
            await self.forward_message(file_hash, user_id)
        else:
            logger.warning(f"User {user_id} needs to join required channels")
            await event.respond(
                self.constants.MANDATORY_JOIN_MESSAGE,
                buttons=await self.get_required_channels_buttons(file_hash)
            )

    async def request_upload_file_user(self, event):
        user = await event.get_sender()
        user_id = user.id
        username = user.username or "بدون نام کاربری"
        logger.info(f"Upload request from user {user_id} ({username})")

        try:
            buttons = [
                [
                    Button.inline("تایید", f"approve_upload:{user_id}"),
                    Button.inline("رد", f"reject_upload:{user_id}")
                ]
            ]

            await self.bot.send_message(
                self.config.super_admin_id,
                self.constants.admin.UPLOAD_REQUEST['NEW'].format(
                    user_id=user_id,
                    username=username
                ),
                buttons=buttons
            )

            await event.respond("درخواست شما برای آپلود فایل ارسال شد. نتیجه به زودی به شما اعلام خواهد شد.")
            logger.debug(f"Upload request notification sent for user {user_id}")

        except Exception as e:
            logger.error(f"Error processing upload request for user {user_id}: {e}", exc_info=True)
            await event.respond(self.constants.ERROR_MESSAGE)

    async def support_user(self, event):
        user_id = event.sender_id
        logger.info(f"Support request from user {user_id}")

        await event.respond(
            self.constants.SUPPORT_PROMPT,
            buttons=[Button.inline(self.constants.CANCEL_COMMAND, b"cancel")]
        )
        self.bot.add_event_handler(
            self._handle_support_message,
            events.NewMessage(chats=event.chat_id, incoming=True)
        )
        logger.debug(f"Support handler added for user {user_id}")

    async def _handle_support_message(self, event):
        message = event.message
        user_id = event.sender_id
        logger.info(f"Support message received from user {user_id}: {message.message}")

        try:
            await self.bot.send_message(
                self.config.super_admin_id,
                f"پیام پشتیبانی از کاربر {user_id}:\n\n{message.message}"
            )
            await event.respond(self.constants.SUPPORT_MESSAGE_SENT)
            logger.debug(f"Support message forwarded for user {user_id}")

        except Exception as e:
            logger.error(f"Error handling support message from user {user_id}: {e}", exc_info=True)
            await event.respond(self.constants.ERROR_MESSAGE)
        finally:
            self.bot.remove_event_handler(self._handle_support_message)
            logger.debug(f"Support handler removed for user {user_id}")

    async def cancel(self, event):
        user_id = event.sender_id
        logger.info(f"Cancel command from user {user_id}")

        try:
            if user_id == self.config.super_admin_id:
                logger.debug("Returning to super admin panel")
                await event.edit(
                    self.constants.CANCEL_COMMAND,
                    buttons=self.keyboards.get_super_admin_panel_buttons()
                )
            elif self.is_admin(user_id):
                logger.debug("Returning to admin panel")
                await event.edit(
                    self.constants.CANCEL_COMMAND,
                    buttons=self.keyboards.get_admin_panel_buttons()
                )
            else:
                logger.debug("Returning to user panel")
                await event.edit(
                    self.constants.CANCEL_COMMAND,
                    buttons=self.keyboards.get_user_buttons()
                )

            # Remove handlers
            self.bot.remove_event_handler(
                self._handle_support_message,
                events.NewMessage(chats=event.chat_id, incoming=True)
            )
            logger.debug(f"All handlers removed for user {user_id}")

        except Exception as e:
            logger.error(f"Error handling cancel command for user {user_id}: {e}", exc_info=True)
