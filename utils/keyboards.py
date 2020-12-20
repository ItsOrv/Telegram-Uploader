from telethon import Button
from config.logger_config import logger

class Keyboards:
    def __init__(self, config):
        self.config = config

    def get_user_buttons(self):
        return [
            [Button.inline("درخواست آپلود فایل", b"request_upload_file")],
            [Button.inline("پشتیبانی", b"support")]
        ]

    def get_admin_panel_buttons(self):
        return [
            [Button.inline("آپلود فایل", b"upload_file_admin")],
            [Button.inline("حذف فایل", b"delete_file_admin")]
        ]

    def get_super_admin_panel_buttons(self):
        return [
            [Button.inline("مدیریت ادمین ها", b"manage_admins")],
            [Button.inline("مدیریت کاربران", b"manage_users")],
            [Button.inline("مدیریت گروه ها", b"manage_groups")],
            [Button.inline("مدیریت کانال ها", b"add_mandatory_channel")],
            [Button.inline("دریافت دیتابیس", b"get_database_file")],
            [Button.inline("ارسال پیام همگانی", b"send_announcement_super_admin")]
        ]
