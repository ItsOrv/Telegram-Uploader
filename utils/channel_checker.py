from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant
from config.logger_config import logger

async def check_channel_membership(bot, user_id, channel_id):
    try:
        result = await bot(GetParticipantRequest(channel_id, user_id))
        if result and result.participant:
            return isinstance(result.participant, ChannelParticipant)
        return False
    except Exception as e:
        logger.debug(f"channel check: user {user_id} not in {channel_id}: {e}")
        return False
