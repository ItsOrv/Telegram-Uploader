from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant
from config.logger_config import logger

async def check_channel_membership(bot, user_id, channel_id):
    try:
        participant = await bot(GetParticipantRequest(channel_id, user_id))
        return isinstance(participant.participant, ChannelParticipant)
    except Exception as e:
        logger.error(f"channel check error: {e}")
        return False
