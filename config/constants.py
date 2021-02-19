from config.logger_config import logger

class FileConstants:
    NOT_FOUND = "فایل مورد نظر یافت نشد."
    DELETE = type('obj', (object,), {'PENDING': "فایل در چند ثانیه دیگر حذف خواهد شد."})()

class AdminConstants:
    UPLOAD_REQUEST = {
        'NEW': "درخواست آپلود جدید:\nکاربر: {user_id}\nیوزرنیم: @{username}"
    }

class SuperAdminConstants:
    WELCOME = "پنل سوپر ادمین"

class UserConstants:
    ERROR = "خطایی رخ داد. لطفا دوباره تلاش کنید."

class Constants:
    WELCOME_MESSAGE = "سلام! به ربات خوش آمدید."
    ADMIN_PANEL_MESSAGE = "پنل مدیریت"
    ERROR_MESSAGE = "خطایی رخ داد. لطفا دوباره تلاش کنید."
    MANDATORY_JOIN_MESSAGE = "برای دریافت فایل باید عضو کانال های زیر باشید:"
    CANCEL_COMMAND = "لغو شد."
    SUPPORT_PROMPT = "پیام خود را بفرستید:"
    SUPPORT_MESSAGE_SENT = "پیام شما ارسال شد."
    SET_GROUP_HELP = "ابتدا گروه اصلی و بکاپ را ست کنید."
    SET_MAIN_GROUP_SUCCESS = "گروه اصلی با موفقیت ست شد."
    SET_BACKUP_GROUP_SUCCESS = "گروه بکاپ با موفقیت ست شد."

    def __init__(self, config=None):
        self.config = config
        self.file = FileConstants()
        self.admin = AdminConstants()
        self.super_admin = SuperAdminConstants()
        self.user = UserConstants()
