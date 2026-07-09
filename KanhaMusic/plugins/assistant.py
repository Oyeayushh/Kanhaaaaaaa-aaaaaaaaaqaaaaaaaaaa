"""
Assistant management commands.
/joinvc   — Make assistant join the current voice chat
/leavevc  — Make assistant leave the current voice chat
/vcstatus — Show current VC status

Uses kanhaCall (core/call.py) — the central VC engine.
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from KanhaMusic.config import Config
from KanhaMusic.core.call import kanhaCall
from KanhaMusic.core.userbot import assistant
from KanhaMusic.database import db
from KanhaMusic.utils.decorators import admin_or_auth, check_blacklist


async def _ensure_assistant_in_group(client: Client, chat_id: int) -> bool:
    """Check if assistant is in the group; if not, try to add them."""
    try:
        me = await assistant.get_me()
        await client.get_chat_member(chat_id, me.id)
        return True
    except Exception:
        try:
            me = await assistant.get_me()
            await client.add_chat_members(chat_id, me.id)
            return True
        except Exception:
            return False


@Client.on_message(filters.command(["joinvc", "join"]) & filters.group)
@check_blacklist
@admin_or_auth
async def joinvc_command(client: Client, message: Message):
    """Make the assistant join the current voice chat."""
    chat_id = message.chat.id
    msg = await message.reply_text("🎙 Joining voice chat...")

    in_group = await _ensure_assistant_in_group(client, chat_id)
    if not in_group:
        return await msg.edit_text(
            "❌ Could not add assistant to the group.\n\n"
            "**Please manually add the assistant account to this group, then try again.**"
        )

    # Join with a silent placeholder stream, then mute immediately
    import asyncio
    ok = await kanhaCall.join_call(
        chat_id,
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        video=False,
    )
    if ok:
        await asyncio.sleep(0.5)
        await kanhaCall.mute_call(chat_id)
        await msg.edit_text(
            "✅ **Assistant joined the Voice Chat!**\n\n"
            "🎙 Use `/play [song]` to start streaming music.\n"
            "📞 Assistant is now ready in VC."
        )
    else:
        await msg.edit_text(
            "❌ **Could not join Voice Chat.**\n\n"
            "Make sure a Voice Chat is active in this group:\n"
            "Group Menu → ··· → Start Voice Chat"
        )


@Client.on_message(filters.command(["leavevc", "leave"]) & filters.group)
@check_blacklist
@admin_or_auth
async def leavevc_command(client: Client, message: Message):
    """Make the assistant leave the current voice chat."""
    chat_id = message.chat.id
    ok = await kanhaCall.leave_call(chat_id)
    db.remove_active(chat_id)
    db.clear_queue(chat_id)
    db.set_pause(chat_id, False)
    if ok:
        await message.reply_text("👋 **Assistant left the Voice Chat.**\n\nMusic has been stopped.")
    else:
        await message.reply_text("ℹ️ Assistant was not in any voice chat.")


@Client.on_message(filters.command(["vcstatus", "vc"]) & filters.group)
@check_blacklist
async def vcstatus_command(client: Client, message: Message):
    """Show current voice chat status."""
    chat_id  = message.chat.id
    active   = db.get_active(chat_id)
    queue    = db.get_queue(chat_id)
    paused   = db.is_paused(chat_id)
    loop_mode= db.get_loop(chat_id)
    volume   = db.get_volume(chat_id)
    loop_str = {0: "❌ Off", 1: "🔁 Single", 2: "🔁 Queue"}.get(loop_mode, "Off")

    if not active:
        return await message.reply_text(
            "📻 **Voice Chat Status**\n\n"
            "❌ Nothing is playing right now.\n\n"
            "Use `/play [song]` to start!"
        )

    from KanhaMusic.plugins.autoplay import is_autoplay_on
    autoplay = "🟢 ON" if is_autoplay_on(chat_id) else "🔴 OFF"

    await message.reply_text(
        f"📻 **Voice Chat Status**\n\n"
        f"🎵 **Now Playing:**\n"
        f"└ {active.get('title', 'Unknown')[:50]}\n"
        f"   ⏱ {active.get('duration', '?')} | 🎤 {active.get('channel', '?')[:25]}\n\n"
        f"📋 **Queue:** {len(queue)} song(s)\n"
        f"▶️ **Status:** {'⏸ Paused' if paused else '▶️ Playing'}\n"
        f"🔁 **Loop:** {loop_str}\n"
        f"🔊 **Volume:** {volume}%\n"
        f"🔄 **Autoplay:** {autoplay}"
    )


# ── Group join handler ────────────────────────────────────────────────────────

@Client.on_message(filters.new_chat_members)
async def new_member_handler(client: Client, message: Message):
    """Welcome message when bot is added to a group."""
    me = await client.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            await message.reply_text(
                f"👋 **Thanks for adding KanhaMusic!** 🎵\n\n"
                f"I stream music in your Voice Chats using an assistant account.\n\n"
                f"**Quick Start:**\n"
                f"1️⃣ Start a Voice Chat in this group\n"
                f"2️⃣ Use `/play [song name]` — I'll join and play!\n\n"
                f"📋 Use `/help` to see all {40}+ commands.\n"
                f"⚙️ Use `/settings` to configure the bot.\n\n"
                f"📞 **Core:** `kanhaCall` — powered by PyTgCalls + Pyrogram"
            )
            break
