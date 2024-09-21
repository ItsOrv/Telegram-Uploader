# Telegram Uploader Bot

This Telegram Uploader Bot allows users to upload and forward messages (including videos, photos, and etc) seamlessly within Telegram. The bot utilizes Telegram's built-in message forwarding capabilities, eliminating the need for downloading and re-uploading files on the server.

## Features

- **Seamless Uploading:** Users can send messages directly to the bot, which forwards them to a specified storage group without downloading and re-uploading the content.
- **Unique Links:** After forwarding a message, the bot generates a unique link that users can share. When someone clicks on the link and starts the bot, they receive the forwarded message.
- **Topic-Based Organization:** Users can request messages based on specific topics. The bot searches through predefined topics and retrieves relevant messages.
- **Admin Management:** Super admins can manage users and settings, including adding or removing channels and managing admin privileges.
- **User Statistics:** The bot tracks the number of messages sent and the users who interacted with it, providing insights for admins.

## Requirements

- A Telegram account and bot token from [BotFather](https://t.me/botfather).
- Python 3.7 or higher.
- The following Python libraries:
  - `telethon`
  - `asyncio`
  - `json`

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ItsOrv/Telegram-Uploader.git
   cd Telegram-Uploader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot:**
   - Update the `config.py` file with your `api_id`, `api_hash`, and `bot_token`.

4. **Run the bot:**
   ```bash
   python main.py
   ```

## Usage

1. **Starting the Bot:**
   - Users can initiate the bot by sending the `/start` command. The bot will check channel memberships and provide instructions accordingly.

2. **Uploading Messages:**
   - Users can send messages (text, photo, or video) to the bot, and the bot will forward them to the designated storage group.

3. **Requesting Messages:**
   - Users can request messages related to specific topics by sending commands in the format:
     ```
     /start topic_name message_content
     ```
   - The bot will search the specified topic and return the relevant message.

4. **Admin Functions:**
   - Admins can manage user permissions, view statistics, and send broadcast messages through the admin panel.

## Notes

- The bot does not download and store files on the server; it simply forwards them, making it efficient and lightweight.
- Users should ensure they are members of any required channels to use the bot's features.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to create an issue or submit a pull request.

