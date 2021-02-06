import functools
from telethon import events
import logging
import json
from enum import Enum, auto
from functools import wraps
from config.logger_config import logger

class UserRole(Enum):
    USER = auto()
    ADMIN = auto()
    SUPER_ADMIN = auto()

class SecurityManager:
    def __init__(self, config):
        self.config = config

    def get_user_role(self, user_id, db):
        if user_id == self.config.super_admin_id:
            return UserRole.SUPER_ADMIN
        if db.is_admin(user_id):
            return UserRole.ADMIN
        return UserRole.USER

    def check_banned(self, user_id, db):
        return db.is_banned(user_id)

def require_roles(*required_roles):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, event, *args, **kwargs):
            user_id = event.sender_id
            try:
                user_role = await check_user_access(self.db, user_id)
                if user_role in required_roles:
                    return await func(self, event, *args, **kwargs)
                else:
                    await event.respond("شما دسترسی لازم برای این عملیات را ندارید.")
                    return None
            except Exception as e:
                logger.error(f"Error checking user access: {e}", exc_info=True)
                await event.respond("خطا در بررسی دسترسی")
                return None
        return wrapper
    return decorator

async def check_user_access(db, user_id: int) -> UserRole:
    try:
        logger.debug(f"Checking access level for user {user_id}")
        if db.is_banned(user_id):
            logger.warning(f"User {user_id} is banned")
            return UserRole.USER
        if user_id == db.config.super_admin_id:
            return UserRole.SUPER_ADMIN
        admin = db.get_admin(user_id)
        if admin:
            return UserRole.ADMIN
        return UserRole.USER
    except Exception as e:
        logger.error(f"Error checking user access level: {e}", exc_info=True)
        return UserRole.USER
