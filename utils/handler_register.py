from telethon import events
from config.logger_config import logger

class HandlerRegistrar:
    def __init__(self, bot, admin_handlers, super_admin_handlers, user_start, start_handlers):
        self.bot = bot
        self.admin_handlers = admin_handlers
        self.super_admin_handlers = super_admin_handlers
        self.user_start = user_start
        self.start_handlers = start_handlers

    def register_handlers(self):
        logger.info("Started registering event handlers")
        try:
            self._register_command_handlers()
            self._register_admin_handlers()
            self._register_super_admin_handlers()
            self._register_user_handlers()
            logger.info("All handlers registered successfully")
        except Exception as e:
            logger.error(f"Error registering handlers: {e}", exc_info=True)
            raise

    def _register_command_handlers(self):
        self.bot.add_event_handler(self.start_handlers.handle_start, events.NewMessage(pattern='/start'))
        self.bot.add_event_handler(self.start_handlers.handle_set_main, events.NewMessage(pattern='/set_main'))
        self.bot.add_event_handler(self.start_handlers.handle_set_backup, events.NewMessage(pattern='/set_backup'))
        self.bot.add_event_handler(
            self.start_handlers.check_subscription_callback,
            events.CallbackQuery(pattern=lambda x: x and (
                x == b"check_subscription" or x.startswith(b"check_subscription:")
            ))
        )

    def _register_admin_handlers(self):
        self.bot.add_event_handler(self.admin_handlers.handle_admin_commands, events.CallbackQuery(data=b"upload_file_admin"))
        self.bot.add_event_handler(self.admin_handlers.handle_admin_commands, events.CallbackQuery(data=b"delete_file_admin"))
        self.bot.add_event_handler(self.admin_handlers.cancel, events.CallbackQuery(data=b"cancel"))

    def _register_super_admin_handlers(self):
        logger.debug("Registering super admin handlers")
        cmds = [
            b"back_to_super_admin_panel", b"back_to_admin_panel",
            b"manage_admins", b"add_admin", b"remove_admin",
            b"manage_users", b"ban_user", b"unban_user", b"view_user_stats",
            b"manage_groups", b"add_group", b"remove_group", b"view_group_stats",
            b"upload_file_super_admin", b"delete_file_super_admin",
            b"add_mandatory_channel", b"remove_mandatory_channel",
            b"get_database_file", b"send_announcement_super_admin",
            b"cancel_add_admin", b"cancel_remove_admin", b"cancel_ban_user",
            b"cancel_unban_user", b"cancel_add_group", b"cancel_remove_group"
        ]
        for cmd in cmds:
            self.bot.add_event_handler(
                self.super_admin_handlers.handle_super_admin_commands,
                events.CallbackQuery(data=cmd)
            )
        for pattern in [b"approve_upload:", b"reject_upload:"]:
            self.bot.add_event_handler(
                self.super_admin_handlers.handle_super_admin_commands,
                events.CallbackQuery(pattern=pattern)
            )

    def _register_user_handlers(self):
        self.bot.add_event_handler(self.user_start.handle_user_commands, events.CallbackQuery(data=b"request_upload_file"))
        self.bot.add_event_handler(self.user_start.handle_user_commands, events.CallbackQuery(data=b"support"))
        self.bot.add_event_handler(
            self.user_start.handle_user_commands,
            events.CallbackQuery(data=lambda data: data.startswith(b"check_membership:"))
        )
