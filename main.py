import json
import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API account information
api_id = 'api_id'
api_hash = 'api_hash'
bot_token = 'bot_token'

# Super admin ID and admin list
super_admin_id = 123456789
admins_file = "admins.json"
admin_ids = []  # List of admins including the super admin

# Default message deletion time (in seconds)
delete_delay_seconds = 30

# Files for storing information
channels_file = "required_channels.json"
banned_users_file = "banned_users.json"
users_file = "users.json"  # File for storing user IDs

# Statistics and reporting variables
sent_files_today = 0
users_today = set()
user_file_count = defaultdict(int)
last_reset_time = datetime.now()

# Topic links
topics = {
    "phisic": "topic link",
    "zist": "topic link",
    "riazi": "topic link",
    "config": "topic link"
}

# Function to load data from a JSON file
def load_json_file(file_path, default_value):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            logger.info(f"Loaded data from {file_path}: {data}")
            return data
    except FileNotFoundError:
        logger.warning(f"No {file_path} file found. Returning default value.")
        return default_value

# Function to save data to a JSON file
def save_json_file(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file)
        logger.info(f"Saved data to {file_path}: {data}")

# Function to load admin list from file
def load_admins():
    return load_json_file(admins_file, [super_admin_id])

# Function to save admin list to file
def save_admins(admins):
    save_json_file(admins_file, admins)

# Load admin list
admin_ids = load_admins()

# Function to load user list from file
def load_users():
    return load_json_file(users_file, [])

# Function to save user list to file
def save_users(users):
    save_json_file(users_file, users)

# Load user list
user_ids = load_users()

# Create bot client
bot = TelegramClient('new_bot_session', api_id, api_hash).start(bot_token=bot_token)

# Manage admin and super admin states
admin_state = {}

# Function to load channel list from file
def load_channels():
    return load_json_file(channels_file, [])

# Function to save channel list to file
def save_channels(channels):
    save_json_file(channels_file, channels)

# New function to check membership in a channel
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

# Function to reset daily statistics if needed
def reset_daily_stats_if_needed():
    global sent_files_today, users_today, last_reset_time
    now = datetime.now()
    if now - last_reset_time >= timedelta(days=1):
        sent_files_today = 0
        users_today.clear()
        last_reset_time = now
        logger.info("Daily stats have been reset.")

# Function to search and forward messages based on content in a specific topic
async def find_and_send_file(event, topic, name):
    global sent_files_today, user_file_count
    try:
        reset_daily_stats_if_needed()

        topic_link = topics.get(topic)
        if not topic_link:
            await event.respond(f"The topic '{topic}' is invalid.")
            return

        parts = topic_link.split('/')
        group_id = parts[4]
        group_entity = await bot.get_entity(int(group_id))
        matched_messages = []

        async for message in bot.iter_messages(group_entity, search=name, limit=None):
            if message.message and name in message.message:
                logger.info(f"Message containing '{name}' found in topic '{topic}'.")
                matched_messages.append(message)

        if matched_messages:
            forwarded_messages = await bot.forward_messages(event.sender_id, matched_messages)
            sent_files_today += len(forwarded_messages)
            user_file_count[event.sender_id] += len(forwarded_messages)
            users_today.add(event.sender_id)
            await event.respond(f"Please forward your file to the saved messages. The file will be deleted in {delete_delay_seconds} seconds.")

            await asyncio.sleep(delete_delay_seconds)
            await bot.delete_messages(event.sender_id, forwarded_messages)
        else:
            logger.info(f"No messages containing '{name}' found in topic '{topic}'.")
            await event.respond("Unfortunately, no video/message has been uploaded yet!")

    except asyncio.TimeoutError:
        logger.error(f"Search for message '{name}' in topic '{topic}' timed out.")
        await event.respond(f"The search for message '{name}' in topic '{topic}' took too long.")

# Handler for the /start command with parameters
@bot.on(events.NewMessage(pattern=r'/start(?: (.+))?'))
async def start(event):
    user_id = event.sender_id
    banned_users = load_json_file(banned_users_file, [])

    if user_id not in user_ids:
        user_ids.append(user_id)
        save_users(user_ids)

    if user_id in banned_users:
        await event.respond("You have been banned from using this bot.")
        return

    logger.info(f"Received /start from user: {user_id}")

    if user_id in admin_ids:
        logger.info(f"User {user_id} is admin, sending admin panel.")
        buttons = [
            [Button.inline("Mandatory Join Settings", b"join_settings")],
        ]
        if user_id == super_admin_id:
            buttons.append([Button.inline("Admin Management", b"admin_management")])
            buttons.append([Button.inline("User Management", b"user_management")])
            buttons.append([Button.inline("Statistics and Reports", b"statistics")])
            buttons.append([Button.inline("Broadcast Message", b"broadcast_message")])
        await event.respond("Welcome to the admin panel.", buttons=buttons)
    else:
        logger.info(f"User {user_id} is not an admin. Checking channel memberships.")
        channels = load_channels()
        not_joined_channels = []

        for channel in channels:
            is_member = await check_membership(user_id, channel)
            if not is_member:
                not_joined_channels.append(channel)

        if not_joined_channels:
            buttons = [[Button.url(f"🔗 Join {channel} Channel", f"https://t.me/{channel}")] for channel in not_joined_channels]
            buttons.append([Button.inline("🔄 Check Membership", b"check_membership")])
            await event.respond(
                "You are not a member of the following channels. Please join these channels first and then check your membership.",
                buttons=buttons
            )
        else:
            await event.respond("You are a member of all mandatory channels and can use the bot.")
            if event.pattern_match.group(1):
                params = event.pattern_match.group(1).split('_')
                if len(params) == 2:
                    topic, name = params
                    await find_and_send_file(event, topic, name)

@bot.on(events.CallbackQuery)
async def callback(event):
    user_id = event.sender_id
    logger.info(f"Received callback from user {user_id} with data: {event.data}")

    if user_id in admin_ids:
        if event.data == b"join_settings":
            await event.respond("Manage mandatory join settings.", buttons=[
                [Button.inline("Add Channel", b"add_channel")],
                [Button.inline("Remove Channel", b"remove_channel")],
                [Button.inline("Back", b"back_to_admin_panel")]
            ])

        elif event.data == b"add_channel":
            await event.respond("Please enter the channel ID:")
            admin_state[user_id] = "awaiting_channel_id"

        elif event.data == b"remove_channel":
            await event.respond("Please enter the channel ID:")
            admin_state[user_id] = "awaiting_remove_channel_id"

        elif event.data == b"admin_management":
            await event.respond("Manage admins.", buttons=[
                [Button.inline("Add Admin", b"add_admin")],
                [Button.inline("Remove Admin", b"remove_admin")],
                [Button.inline("Back", b"back_to_admin_panel")]
            ])

        elif event.data == b"user_management":
            await event.respond("Manage users.", buttons=[
                [Button.inline("List Users", b"list_users")],
                [Button.inline("Remove User", b"remove_user")],
                [Button.inline("Back", b"back_to_admin_panel")]
            ])

        elif event.data == b"statistics":
            await event.respond(f"Total files sent today: {sent_files_today}\nTotal users: {len(users_today)}")

        elif event.data == b"broadcast_message":
            await event.respond("Please enter the broadcast message:")
            admin_state[user_id] = "awaiting_broadcast_message"

    else:
        await event.answer("You are not an admin.", alert=True)

# Handler to receive input from admins
@bot.on(events.NewMessage(incoming=True))
async def admin_input(event):
    user_id = event.sender_id

    if user_id in admin_ids and user_id in admin_state:
        state = admin_state[user_id]

        if state == "awaiting_channel_id":
            channel_id = event.raw_text
            channels = load_channels()
            channels.append(channel_id)
            save_channels(channels)
            await event.respond(f"Channel '{channel_id}' has been added to the channel list.")
            del admin_state[user_id]

        elif state == "awaiting_remove_channel_id":
            channel_id = event.raw_text
            channels = load_channels()
            if channel_id in channels:
                channels.remove(channel_id)
                save_channels(channels)
                await event.respond(f"Channel '{channel_id}' has been removed from the channel list.")
            else:
                await event.respond(f"Channel '{channel_id}' does not exist in the list.")
            del admin_state[user_id]

        elif state == "awaiting_broadcast_message":
            message = event.raw_text
            users = load_users()
            for user in users:
                try:
                    await bot.send_message(user, message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user}: {e}")
            await event.respond("Broadcast message sent.")
            del admin_state[user_id]

# Handler for sending broadcast messages
@bot.on(events.NewMessage(pattern='/broadcast'))
async def send_broadcast(event):
    if event.sender_id in admin_ids:
        await event.respond("Please enter the broadcast message:")
        admin_state[event.sender_id] = "awaiting_broadcast_message"

# Run the bot
if __name__ == '__main__':
    bot.run_until_disconnected()
