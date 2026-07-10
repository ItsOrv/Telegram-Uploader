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
                    await _notify_super_admin(self, event, func.__name__, user_id, user_role, required_roles)
                    return None
            except Exception as e:
                logger.error(f"Error checking user access: {e}", exc_info=True)
                await event.respond("خطا در بررسی دسترسی")
                return None
        return wrapper
    return decorator

async def _notify_super_admin(handler, event, func_name, user_id, user_role, required_roles):
    """Send a security alert to the super admin on an unauthorized handler call."""
    try:
        super_admin_id = handler.config.super_admin_id
        if user_id == super_admin_id:
            return
        needed = ", ".join(r.name for r in required_roles)
        try:
            command = event.data.decode('utf-8')
        except Exception:
            command = getattr(getattr(event, 'message', None), 'message', func_name)
        alert = (
            "هشدار امنیتی: فراخوانی غیرمجاز\n"
            f"کاربر: {user_id}\n"
            f"رول کاربر: {user_role.name}\n"
            f"هندلر: {func_name}\n"
            f"دستور: {command}\n"
            f"رول لازم: {needed}"
        )
        await handler.bot.send_message(super_admin_id, alert)
        logger.warning(f"Unauthorized call to {func_name} by {user_id} ({user_role.name}); super admin alerted")
    except Exception as e:
        logger.error(f"Failed to send security alert: {e}", exc_info=True)

async def check_user_access(db, user_id: int) -> UserRole:
    try:
        logger.debug(f"Checking access level for user {user_id}")
        if db.is_banned(user_id):
            logger.warning(f"User {user_id} is banned")
            return UserRole.USER
        if user_id == db.config.super_admin_id:
            logger.debug(f"User {user_id} is super admin")
            return UserRole.SUPER_ADMIN
        admin = db.get_admin(user_id)
        if admin:
            return UserRole.ADMIN
        return UserRole.USER
    except Exception as e:
        logger.error(f"Error checking user access level: {e}", exc_info=True)
        return UserRole.USER
