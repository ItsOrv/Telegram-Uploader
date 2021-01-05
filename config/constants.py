class Constants:
    WELCOME_MESSAGE = "سلام! به ربات خوش آمدید."
    ADMIN_PANEL_MESSAGE = "پنل مدیریت"
    ERROR_MESSAGE = "خطایی رخ داد. لطفا دوباره تلاش کنید."
    MANDATORY_JOIN_MESSAGE = "برای دریافت فایل باید عضو کانال های زیر باشید:"
    CANCEL_COMMAND = "لغو شد."
    SUPPORT_PROMPT = "پیام خود را بفرستید:"
    SUPPORT_MESSAGE_SENT = "پیام شما ارسال شد."

    def __init__(self, config=None):
        self.config = config
