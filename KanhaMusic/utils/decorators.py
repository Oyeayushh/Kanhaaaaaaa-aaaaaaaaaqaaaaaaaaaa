"""
Decorators used across KanhaMusic plugins.
"""

from functools import wraps

from pyrogram import Client
from pyrogram.types import Message

from KanhaMusic.config import Config
from KanhaMusic.database import db
from KanhaMusic.strings import get_string


def owner_only(func):
    """Restrict command to bot owner only."""
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if message.from_user and message.from_user.id == Config.OWNER_ID:
            return await func(client, message, *args, **kwargs)
        await message.reply_text(get_string["not_owner"])
    return wrapper


def admin_or_auth(func):
    """Allow admins, auth users, and owner."""
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if not message.from_user:
            return
        user_id = message.from_user.id
        chat_id = message.chat.id

        if user_id == Config.OWNER_ID:
            return await func(client, message, *args, **kwargs)

        if db.is_auth_user(chat_id, user_id):
            return await func(client, message, *args, **kwargs)

        try:
            member = await client.get_chat_member(chat_id, user_id)
            from pyrogram.enums import ChatMemberStatus
            if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                return await func(client, message, *args, **kwargs)
        except Exception:
            pass

        await message.reply_text(get_string["not_admin"])
    return wrapper


def check_blacklist(func):
    """Check if user is globally banned."""
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if message.from_user and db.is_gbanned(message.from_user.id):
            await message.reply_text(get_string["gbanned_user"])
            return
        return await func(client, message, *args, **kwargs)
    return wrapper
