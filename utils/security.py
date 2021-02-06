from enum import Enum, auto
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
