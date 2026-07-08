"""
Admin commands: /auth, /unauth, /authlist, /gban, /ungban, /gbanlist
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from KanhaMusic.config import Config
from KanhaMusic.database import db
from KanhaMusic.strings import get_string
from KanhaMusic.utils.decorators import admin_or_auth, owner_only, check_blacklist


@Client.on_message(filters.command(["auth"]) & filters.group)
@check_blacklist
async def auth_command(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    try:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(chat_id, user_id)
        is_admin = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        is_admin = False

    if user_id != Config.OWNER_ID and not is_admin:
        await message.reply_text(get_string["not_admin"])
        return

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target = await client.get_users(target_id)
        except Exception:
            await message.reply_text("❌ Could not find user.")
            return

    if not target:
        await message.reply_text("❌ Reply to a user or provide user ID.")
        return

    if db.is_auth_user(chat_id, target.id):
        await message.reply_text(get_string["already_auth"])
        return

    db.add_auth_user(chat_id, target.id)
    await message.reply_text(
        f"✅ **{target.mention}** has been authorized to use KanhaMusic commands in this group."
    )


@Client.on_message(filters.command(["unauth"]) & filters.group)
@check_blacklist
async def unauth_command(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0

    try:
        from pyrogram.enums import ChatMemberStatus
        member = await client.get_chat_member(chat_id, user_id)
        is_admin = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        is_admin = False

    if user_id != Config.OWNER_ID and not is_admin:
        await message.reply_text(get_string["not_admin"])
        return

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            target = await client.get_users(target_id)
        except Exception:
            await message.reply_text("❌ Could not find user.")
            return

    if not target:
        await message.reply_text("❌ Reply to a user or provide user ID.")
        return

    if not db.is_auth_user(chat_id, target.id):
        await message.reply_text(get_string["not_auth"])
        return

    db.remove_auth_user(chat_id, target.id)
    await message.reply_text(
        f"✅ **{target.mention}** has been unauthorized in this group."
    )


@Client.on_message(filters.command(["authlist"]) & filters.group)
@check_blacklist
async def authlist_command(client: Client, message: Message):
    chat_id = message.chat.id
    auth_list = db.get_auth_users(chat_id)

    if not auth_list:
        await message.reply_text("📭 No authorized users in this group.")
        return

    text = "👥 **Authorized Users:**\n\n"
    for uid in auth_list:
        try:
            user = await client.get_users(uid)
            text += f"• {user.mention} (`{uid}`)\n"
        except Exception:
            text += f"• `{uid}`\n"

    await message.reply_text(text)


@Client.on_message(filters.command(["gban"]) & filters.private)
@owner_only
async def gban_command(client: Client, message: Message):
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(int(message.command[1]))
        except Exception:
            await message.reply_text("❌ Could not find user.")
            return

    if not target:
        await message.reply_text("❌ Reply to a user or provide user ID.")
        return

    if target.id == Config.OWNER_ID:
        await message.reply_text("❌ Cannot ban the owner!")
        return

    db.gban_user(target.id)
    await message.reply_text(
        f"🔨 **{target.mention}** has been globally banned from KanhaMusic."
    )


@Client.on_message(filters.command(["ungban"]) & filters.private)
@owner_only
async def ungban_command(client: Client, message: Message):
    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(int(message.command[1]))
        except Exception:
            await message.reply_text("❌ Could not find user.")
            return

    if not target:
        await message.reply_text("❌ Reply to a user or provide user ID.")
        return

    if not db.is_gbanned(target.id):
        await message.reply_text("⚠️ User is not globally banned.")
        return

    db.ungban_user(target.id)
    await message.reply_text(
        f"✅ **{target.mention}** has been globally unbanned."
    )


@Client.on_message(filters.command(["gbanlist"]) & filters.private)
@owner_only
async def gbanlist_command(client: Client, message: Message):
    gbanned = db.gbanned_users
    if not gbanned:
        await message.reply_text("📭 No globally banned users.")
        return
    text = "🚫 **Globally Banned Users:**\n\n"
    for uid in gbanned:
        try:
            user = await client.get_users(uid)
            text += f"• {user.mention} (`{uid}`)\n"
        except Exception:
            text += f"• `{uid}`\n"
    await message.reply_text(text)
