import json
import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant

# تنظیمات logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# اطلاعات حساب کاربری API
api_id = 'api id'
api_hash = 'api hash'
bot_token = 'bot token'

# اطلاعات حساب کاربری
user_phone = '+1XXXXXXXXXX'  # شماره تلفن حساب کاربری
user_session = 'user_session'  # نام فایل session برای کاربر

# آیدی عددی سوپر ادمین و لیست ادمین‌ها
super_admin_id = Superadminid
admins_file = "admins.json"
admin_ids = []  # لیست ادمین‌ها شامل سوپر ادمین

# زمان پیش‌فرض برای حذف پیام‌ها (بر اساس ثانیه)
delete_delay_seconds = 30

# فایل‌ها برای ذخیره اطلاعات
channels_file = "required_channels.json"
banned_users_file = "banned_users.json"
users_file = "users.json"  # فایل برای ذخیره شناسه کاربران

# متغیرهای آمار و گزارشات
sent_files_today = 0
users_today = set()
user_file_count = defaultdict(int)
last_reset_time = datetime.now()

# لیست تاپیک‌ها و لینک‌های آنها
topics = {
    "phisic": "topic link",
    "zist": "topic link",
    "riazi": "topic link",
    "config":"topic link"
}

# تابع برای بارگذاری اطلاعات از فایل
def load_json_file(file_path, default_value):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            logger.info(f"Loaded data from {file_path}: {data}")
            return data
    except FileNotFoundError:
        logger.warning(f"No {file_path} file found. Returning default value.")
        return default_value

# تابع برای ذخیره اطلاعات به فایل
def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file)
        logger.info(f"Saved data to {file_path}: {data}")

# تابع برای بارگذاری لیست ادمین‌ها از فایل
def load_admins():
    return load_json_file(admins_file, [super_admin_id])

# تابع برای ذخیره لیست ادمین‌ها به فایل
def save_admins(admins):
    save_json_file(admins_file, admins)

# بارگذاری لیست ادمین‌ها
admin_ids = load_admins()

# تابع برای بارگذاری لیست کاربران از فایل
def load_users():
    return load_json_file(users_file, [])

# تابع برای ذخیره لیست کاربران به فایل
def save_users(users):
    save_json_file(users_file, users)

# بارگذاری لیست کاربران
user_ids = load_users()

# نام جدید برای فایل session
bot = TelegramClient('new_bot_session', api_id, api_hash).start(bot_token=bot_token)


# ایجاد کلاینت حساب کاربری
user_client = TelegramClient(user_session, api_id, api_hash)

# مدیریت مراحل ادمین‌ها و سوپر ادمین
admin_state = {}

# تابع برای بارگذاری لیست کانال‌ها از فایل
def load_channels():
    return load_json_file(channels_file, [])

# تابع برای ذخیره لیست کانال‌ها به فایل
def save_channels(channels):
    save_json_file(channels_file, channels)

# تابع جدید برای بررسی عضویت
async def check_membership(user_id, channel_username):
    try:
        result = await bot(GetParticipantRequest(channel=channel_username, participant=user_id))
        if isinstance(result.participant, ChannelParticipant):
            logger.info(f"User {user_id} is a member of {channel_username}.")
            return True
        logger.info(f"User {user_id} is NOT a member of {channel_username}.")
        return False
    except Exception as e:
        logger.error(f"Error while checking membership in {channel_username} for user {user_id}: {e}")
        return False

# تابع برای به‌روزرسانی آمار روزانه
def reset_daily_stats_if_needed():
    global sent_files_today, users_today, last_reset_time
    now = datetime.now()
    if now - last_reset_time >= timedelta(days=1):
        sent_files_today = 0
        users_today.clear()
        last_reset_time = now
        logger.info("Daily stats have been reset.")

# تابع برای جستجو و فوروارد پیام بر اساس محتوای پیام در یک تاپیک خاص
async def find_and_send_file(event, topic, name):
    global sent_files_today, user_file_count
    try:
        reset_daily_stats_if_needed()  # Reset daily stats if needed
        await user_client.connect()
        if not await user_client.is_user_authorized():
            await user_client.send_code_request(user_phone)
            await user_client.sign_in(user_phone, input('Enter the code: '))

        topic_link = topics.get(topic)
        if not topic_link:
            await event.respond(f"تاپیک '{topic}' معتبر نیست.")
            return

        # استخراج شناسه گروه از لینک
        parts = topic_link.split('/')
        group_id = parts[4]

        group_entity = await user_client.get_entity(int(group_id))
        matched_messages = []

        # جستجو در تمامی پیام‌ها بدون محدودیت
        async for message in user_client.iter_messages(group_entity, search=name, limit=None):
            if message.message and name in message.message:
                logger.info(f"Message containing '{name}' found in topic '{topic}'.")
                matched_messages.append(message)

        if matched_messages:
            forwarded_messages = await bot.forward_messages(event.sender_id, matched_messages)
            sent_files_today += len(forwarded_messages)  # Update the count of sent files today
            user_file_count[event.sender_id] += len(forwarded_messages)  # Update the count of files received by the user
            users_today.add(event.sender_id)  # Add user to today's active users

            # Send the warning message about deleting the files
            await event.respond(f"لطفا فایل خود را به پیام‌های ذخیره‌شده فوروارد کنید. حذف فایل تا {delete_delay_seconds} ثانیه دیگر.")

            # Wait for the set delay and then delete the forwarded messages
            await asyncio.sleep(delete_delay_seconds)
            await bot.delete_messages(event.sender_id, forwarded_messages)

        else:
            logger.info(f"No messages containing '{name}' found in topic '{topic}'.")
            await event.respond(f"متاسفانه هنوز فیلم/پیامی آپلود نشده است! ")
    except asyncio.TimeoutError:
        logger.error(f"Search for message '{name}' in topic '{topic}' timed out.")
        await event.respond(f"جستجوی پیام '{name}' در تاپیک '{topic}' بیش از حد مجاز طول کشید.")
    finally:
        await user_client.disconnect()

# هندلر برای دستور /start با پارامتر
@bot.on(events.NewMessage(pattern=r'/start(?: (.+))?'))
async def start(event):
    user_id = event.sender_id
    banned_users = load_json_file(banned_users_file, [])

    # اضافه کردن شناسه کاربر به لیست کاربران اگر قبلاً اضافه نشده باشد
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_users(user_ids)

    if user_id in banned_users:
        await event.respond("شما از استفاده از این ربات مسدود شده‌اید.")
        return

    logger.info(f"Received /start from user: {user_id}")

    if user_id in admin_ids:
        logger.info(f"User {user_id} is admin, sending admin panel.")
        buttons = [
            [Button.inline("تنظیمات جوین اجباری", b"join_settings")],
        ]
        if user_id == super_admin_id:
            buttons.append([Button.inline("مدیریت ادمین‌ها", b"admin_management")])
            buttons.append([Button.inline("مدیریت کاربران", b"user_management")])
            buttons.append([Button.inline("آمار و گزارشات", b"statistics")])
            buttons.append([Button.inline("ارسال پیام همگانی", b"broadcast_message")])  # دکمه پیام همگانی اضافه شد
        await event.respond("به پنل ادمین خوش آمدید.", buttons=buttons)
    else:
        logger.info(f"User {user_id} is not an admin. Checking channel memberships.")
        channels = load_channels()
        not_joined_channels = []

        for channel in channels:
            is_member = await check_membership(user_id, channel)
            if not is_member:
                not_joined_channels.append(channel)

        if not_joined_channels:
            logger.info(f"User {user_id} is not a member of channels: {not_joined_channels}")
            buttons = [[Button.url(f"🔗 عضویت در کانال {channel}", f"https://t.me/{channel}")] for channel in not_joined_channels]
            buttons.append([Button.inline("🔄 بررسی عضویت", b"check_membership")])
            await event.respond(
                "شما هنوز عضو کانال‌های زیر نیستید. لطفاً ابتدا به این کانال‌ها بپیوندید و سپس عضویت خود را بررسی کنید.",
                buttons=buttons
            )
        else:
            logger.info(f"User {user_id} is a member of all required channels.")
            await event.respond("شما عضو تمام کانال‌های اجباری هستید و می‌توانید از ربات استفاده کنید.")
            # ارسال پیام خوش‌آمدگویی
            await event.respond("به ربات خوش آمدید! از خدمات ما استفاده کنید.")

            # چک کردن پارامترهای لینک start
            if event.pattern_match.group(1):
                params = event.pattern_match.group(1).split('_')
                if len(params) == 2:
                    topic, name = params
                    await find_and_send_file(event, topic, name)

# هندلر برای دکمه‌های مربوط به تنظیمات جوین اجباری و مدیریت ادمین‌ها
@bot.on(events.CallbackQuery)
async def callback(event):
    user_id = event.sender_id
    logger.info(f"Received callback from user {user_id} with data: {event.data}")

    if user_id in admin_ids:
        if event.data == b"join_settings":
            logger.info(f"User {user_id} accessed join settings.")
            buttons = [
                [Button.inline("➕ افزودن کانال", b"add_channel")],
                [Button.inline("➖ حذف کانال", b"remove_channel")],
                [Button.inline("⬆️ ارتقا اولویت", b"move_up_channel")],
                [Button.inline("⬇️ کاهش اولویت", b"move_down_channel")],
                [Button.inline("📋 لیست کانال‌ها", b"list_channels")],
                [Button.inline("↩️ بازگشت", b"admin_panel")],
            ]
            await event.respond("تنظیمات جوین اجباری:", buttons=buttons)

        elif event.data == b"admin_management" and user_id == super_admin_id:
            logger.info(f"User {user_id} accessed admin management.")
            buttons = [
                [Button.inline("➕ افزودن ادمین", b"add_admin")],
                [Button.inline("➖ حذف ادمین", b"remove_admin")],
                [Button.inline("📋 لیست ادمین‌ها", b"list_admins")],
                [Button.inline("⏱ تنظیم زمان حذف فایل", b"set_delete_delay")],
                [Button.inline("↩️ بازگشت", b"admin_panel")],
            ]
            await event.respond("مدیریت ادمین‌ها:", buttons=buttons)

        elif event.data == b"user_management" and user_id == super_admin_id:
            logger.info(f"User {user_id} accessed user management.")
            buttons = [
                [Button.inline("🚫 مسدود کردن کاربر", b"ban_user")],
                [Button.inline("♻️ رفع مسدودی کاربر", b"unban_user")],
                [Button.inline("📋 لیست کاربران مسدود", b"list_banned_users")],
                [Button.inline("↩️ بازگشت", b"admin_panel")],
            ]
            await event.respond("مدیریت کاربران:", buttons=buttons)

        elif event.data == b"statistics" and user_id == super_admin_id:
            logger.info(f"User {user_id} accessed statistics.")
            reset_daily_stats_if_needed()  # Reset stats if needed
            top_users = sorted(user_file_count.items(), key=lambda x: x[1], reverse=True)[:3]
            top_users_text = "\n".join([f"User {user}: {count} files" for user, count in top_users])
            await event.respond(
                f"آمار و گزارشات:\n"
                f"تعداد فایل‌های ارسال‌شده امروز: {sent_files_today}\n"
                f"تعداد کاربران امروز: {len(users_today)}\n"
                f"سه نفر برتر در دریافت فایل:\n{top_users_text if top_users else 'هنوز هیچ فایلی ارسال نشده است.'}"
            )

        elif event.data == b"broadcast_message" and user_id == super_admin_id:  # هندلر پیام همگانی اضافه شد
            logger.info(f"User {user_id} initiated broadcast message.")
            admin_state[user_id] = 'broadcast_message'
            await event.respond("لطفاً پیام خود را برای ارسال به تمامی کاربران وارد کنید:")

        elif event.data == b"add_channel":
            logger.info(f"User {user_id} initiated adding a channel.")
            admin_state[user_id] = 'adding_channel'
            await event.respond("نام کاربری (username) کانالی که می‌خواهید اضافه کنید را وارد کنید:")

        elif event.data == b"remove_channel":
            logger.info(f"User {user_id} initiated removing a channel.")
            admin_state[user_id] = 'removing_channel'
            await event.respond("نام کاربری (username) کانالی که می‌خواهید حذف کنید را وارد کنید:")

        elif event.data == b"move_up_channel":
            logger.info(f"User {user_id} initiated moving a channel up.")
            admin_state[user_id] = 'moving_up_channel'
            await event.respond("نام کاربری (username) کانالی که می‌خواهید اولویتش را بالا ببرید را وارد کنید:")

        elif event.data == b"move_down_channel":
            logger.info(f"User {user_id} initiated moving a channel down.")
            admin_state[user_id] = 'moving_down_channel'
            await event.respond("نام کاربری (username) کانالی که می‌خواهید اولویتش را پایین بیاورید را وارد کنید:")

        elif event.data == b"list_channels":
            channels = load_channels()
            if channels:
                logger.info(f"User {user_id} requested the list of required channels.")
                await event.respond("کانال‌های جوین اجباری:\n" + "\n".join([f"@{ch}" for ch in channels]))
            else:
                logger.info(f"User {user_id} requested the list of channels, but no channels are configured.")
                await event.respond("هیچ کانالی در لیست جوین اجباری وجود ندارد.")

        elif event.data == b"add_admin" and user_id == super_admin_id:
            logger.info(f"User {user_id} initiated adding an admin.")
            admin_state[user_id] = 'adding_admin'
            await event.respond("آیدی عددی ادمینی که می‌خواهید اضافه کنید را وارد کنید:")

        elif event.data == b"remove_admin" and user_id == super_admin_id:
            logger.info(f"User {user_id} initiated removing an admin.")
            admin_state[user_id] = 'removing_admin'
            await event.respond("آیدی عددی ادمینی که می‌خواهید حذف کنید را وارد کنید:")

        elif event.data == b"list_admins" and user_id == super_admin_id:
            logger.info(f"User {user_id} requested the list of admins.")
            admins_text = "\n".join([str(admin) for admin in admin_ids])
            await event.respond(f"لیست ادمین‌ها:\n{admins_text}")

        elif event.data == b"ban_user" and user_id == super_admin_id:
            logger.info(f"User {user_id} initiated banning a user.")
            admin_state[user_id] = 'banning_user'
            await event.respond("آیدی عددی کاربری که می‌خواهید مسدود کنید را وارد کنید:")

        elif event.data == b"unban_user" and user_id == super_admin_id:
            logger.info(f"User {user_id} initiated unbanning a user.")
            admin_state[user_id] = 'unbanning_user'
            await event.respond("آیدی عددی کاربری که می‌خواهید از مسدودی خارج کنید را وارد کنید:")

        elif event.data == b"list_banned_users" and user_id == super_admin_id:
            banned_users = load_json_file(banned_users_file, [])
            if banned_users:
                logger.info(f"User {user_id} requested the list of banned users.")
                banned_users_text = "\n".join([str(user) for user in banned_users])
                await event.respond(f"لیست کاربران مسدود:\n{banned_users_text}")
            else:
                await event.respond("هیچ کاربری مسدود نشده است.")

        elif event.data == b"set_delete_delay" and user_id == super_admin_id:
            logger.info(f"User {user_id} initiated setting delete delay.")
            admin_state[user_id] = 'setting_delete_delay'
            await event.respond("لطفاً زمان حذف فایل را به ثانیه وارد کنید:")

        elif event.data == b"admin_panel":
            logger.info(f"User {user_id} returned to admin panel.")
            buttons = [
                [Button.inline("تنظیمات جوین اجباری", b"join_settings")],
            ]
            if user_id == super_admin_id:
                buttons.append([Button.inline("مدیریت ادمین‌ها", b"admin_management")])
                buttons.append([Button.inline("مدیریت کاربران", b"user_management")])
                buttons.append([Button.inline("آمار و گزارشات", b"statistics")])
                buttons.append([Button.inline("ارسال پیام همگانی", b"broadcast_message")])  # دکمه پیام همگانی اضافه شد
            await event.respond("به پنل ادمین خوش آمدید.", buttons=buttons)

@bot.on(events.NewMessage)
async def handle_admin_input(event):
    user_id = event.sender_id
    state = admin_state.get(user_id)
    if user_id == super_admin_id and state is not None:
        target = event.text.strip()
        channels = load_channels()

        if state == 'broadcast_message':  # هندلر دریافت پیام همگانی اضافه شد
            message_text = event.text.strip()
            logger.info(f"User {user_id} is broadcasting a message: {message_text}")

            # ارسال پیام به تمام کاربرانی که ربات را استارت کرده‌اند
            for uid in user_ids:
                try:
                    await bot.send_message(uid, message_text)
                    logger.info(f"Message sent to user {uid}.")
                except Exception as e:
                    logger.error(f"Failed to send message to user {uid}: {e}")

            await event.respond("پیام شما به تمامی کاربران ارسال شد.")
            admin_state.pop(user_id, None)
        
        # باقی کدهای دیگر برای مدیریت سایر state‌ها
        elif state == 'adding_admin':
            target_id = int(target)
            logger.info(f"User {user_id} is adding admin {target_id}.")
            if target_id not in admin_ids:
                admin_ids.append(target_id)
                save_admins(admin_ids)
                await event.respond(f"ادمین {target_id} به لیست ادمین‌ها اضافه شد.")
            else:
                logger.info(f"Admin {target_id} already exists in the list.")
                await event.respond(f"ادمین {target_id} در حال حاضر در لیست وجود دارد.")

        elif state == 'removing_admin':
            target_id = int(target)
            logger.info(f"User {user_id} is removing admin {target_id}.")
            if target_id in admin_ids and target_id != super_admin_id:
                admin_ids.remove(target_id)
                save_admins(admin_ids)
                await event.respond(f"ادمین {target_id} از لیست ادمین‌ها حذف شد.")
            else:
                logger.info(f"Admin {target_id} does not exist in the list or is the super admin.")
                await event.respond(f"ادمین {target_id} در لیست وجود ندارد یا سوپر ادمین است.")

        elif state == 'banning_user':
            target_id = int(target)
            logger.info(f"User {user_id} is banning user {target_id}.")
            banned_users = load_json_file(banned_users_file, [])
            if target_id not in banned_users:
                banned_users.append(target_id)
                save_json_file(banned_users_file, banned_users)
                await event.respond(f"کاربر {target_id} مسدود شد.")
            else:
                await event.respond(f"کاربر {target_id} قبلاً مسدود شده است.")

        elif state == 'unbanning_user':
            target_id = int(target)
            logger.info(f"User {user_id} is unbanning user {target_id}.")
            banned_users = load_json_file(banned_users_file, [])
            if target_id in banned_users:
                banned_users.remove(target_id)
                save_json_file(banned_users_file, banned_users)
                await event.respond(f"کاربر {target_id} از مسدودی خارج شد.")
            else:
                await event.respond(f"کاربر {target_id} در لیست مسدودها نیست.")

        elif state == 'moving_up_channel':
            logger.info(f"User {user_id} is moving up channel {target}.")
            if target in channels:
                index = channels.index(target)
                if index > 0:
                    channels[index], channels[index - 1] = channels[index - 1], channels[index]
                    save_channels(channels)
                    await event.respond(f"کانال {target} به بالا منتقل شد.")
                else:
                    await event.respond(f"کانال {target} در اولویت بالاترین است.")
            else:
                await event.respond(f"کانال {target} در لیست وجود ندارد.")

        elif state == 'moving_down_channel':
            logger.info(f"User {user_id} is moving down channel {target}.")
            if target in channels:
                index = channels.index(target)
                if index < len(channels) - 1:
                    channels[index], channels[index + 1] = channels[index + 1], channels[index]
                    save_channels(channels)
                    await event.respond(f"کانال {target} به پایین منتقل شد.")
                else:
                    await event.respond(f"کانال {target} در آخرین اولویت است.")
            else:
                await event.respond(f"کانال {target} در لیست وجود ندارد.")

        elif state == 'setting_delete_delay':
            try:
                global delete_delay_seconds
                delete_delay_seconds = int(target)
                logger.info(f"User {user_id} set the delete delay to {delete_delay_seconds} seconds.")
                await event.respond(f"زمان حذف فایل به {delete_delay_seconds} ثانیه تنظیم شد.")
            except ValueError:
                await event.respond("مقدار وارد شده معتبر نیست. لطفاً یک عدد صحیح وارد کنید.")

        elif state == 'adding_channel':
            logger.info(f"User {user_id} is adding channel {target}.")
            if target not in channels:
                channels.append(target)
                save_channels(channels)
                await event.respond(f"کانال {target} به لیست کانال‌های جوین اجباری اضافه شد.")
            else:
                logger.info(f"Channel {target} already exists in the list.")
                await event.respond(f"کانال {target} در حال حاضر در لیست وجود دارد.")

        elif state == 'removing_channel':
            logger.info(f"User {user_id} is removing channel {target}.")
            if target in channels:
                channels.remove(target)
                save_channels(channels)
                await event.respond(f"کانال {target} از لیست کانال‌های جوین اجباری حذف شد.")
            else:
                logger.info(f"Channel {target} does not exist in the list.")
                await event.respond(f"کانال {target} در لیست وجود ندارد.")

        # پاک کردن حالت کاربر پس از اتمام عملیات
        admin_state.pop(user_id, None)

# اجرای ربات
bot.start()
user_client.start()
bot.run_until_disconnected()
