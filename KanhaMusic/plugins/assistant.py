"""
Assistant management commands.
/joinvc   — Make assistant join the current voice chat
/leavevc  — Make assistant leave the current voice chat
/vcstatus — Show current VC status

The assistant (userbot) must be a member of the group before it can join VC.
The bot will automatically invite the assistant when needed.
"""

from pyrogram import Client, filters
from pyrogram.types import Message

from KanhaMusic.config import Config
from KanhaMusic.core.call import call_py
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
        except Exception as e:
            return False


@Client.on_message(filters.command(["joinvc", "join"]) & filters.group)
@check_blacklist
@admin_or_auth
async def joinvc_command(client: Client, message: Message):
    """Make the assistant join the current voice chat."""
    chat_id = message.chat.id
    msg = await message.reply_text("🎙 Joining voice chat...")

    # Ensure assistant is a group member
    in_group = await _ensure_assistant_in_group(client, chat_id)
    if not in_group:
        return await msg.edit_text(
            "❌ Could not add assistant to the group.\n\n"
            "**Please manually add the assistant account to this group first.**"
        )

    try:
        from pytgcalls.types.input_stream import AudioPiped
        import asyncio

        # Join with silence stream (no audio)
        await call_py.join_group_call(
            chat_id,
            AudioPiped("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"),
            stream_type=None,
        )
        # Immediately mute (silent VC presence)
        await asyncio.sleep(0.5)
        try:
            await call_py.mute_stream(chat_id)
        except Exception:
            pass

        await msg.edit_text(
            "✅ **Assistant joined the Voice Chat!**\n\n"
            "🎙 Use `/play [song]` to start streaming music.\n"
            "📞 **Assistant** is now ready in VC."
        )
    except Exception as e:
        err = str(e).lower()
        if "no active group call" in err or "groupcall_forbidden" in err:
            await msg.edit_text(
                "❌ **No active voice chat found!**\n\n"
                "Please start a Voice Chat in this group first:\n"
                "Group → ···→ Start Voice Chat"
            )
        elif "already" in err:
            await msg.edit_text("ℹ️ Assistant is **already** in the voice chat.")
        else:
            await msg.edit_text(f"❌ Error joining VC: `{e}`")


@Client.on_message(filters.command(["leavevc", "leave"]) & filters.group)
@check_blacklist
@admin_or_auth
async def leavevc_command(client: Client, message: Message):
    """Make the assistant leave the current voice chat."""
    chat_id = message.chat.id
    try:
        await call_py.leave_group_call(chat_id)
        db.remove_active(chat_id)
        db.clear_queue(chat_id)
        db.set_pause(chat_id, False)
        await message.reply_text(
            "👋 **Assistant left the Voice Chat.**\n\n"
            "Music has been stopped."
        )
    except Exception as e:
        err = str(e).lower()
        if "not in" in err or "groupcall" in err:
            await message.reply_text("ℹ️ Assistant is **not** in any voice chat.")
        else:
            await message.reply_text(f"❌ Error leaving VC: `{e}`")


@Client.on_message(filters.command(["vcstatus", "vc"]) & filters.group)
@check_blacklist
async def vcstatus_command(client: Client, message: Message):
    """Show current voice chat status."""
    chat_id = message.chat.id
    active = db.get_active(chat_id)
    queue = db.get_queue(chat_id)
    is_paused = db.is_paused(chat_id)
    loop_mode = db.get_loop(chat_id)
    volume = db.get_volume(chat_id)

    loop_str = {0: "Off", 1: "🔁 Single", 2: "🔁 Queue"}.get(loop_mode, "Off")

    if not active:
        await message.reply_text(
            "📻 **Voice Chat Status**\n\n"
            "❌ No music is currently playing.\n\n"
            "Use `/play [song]` to start!"
        )
        return

    from KanhaMusic.plugins.autoplay import is_autoplay_on
    autoplay = "🟢 ON" if is_autoplay_on(chat_id) else "🔴 OFF"

    text = (
        f"📻 **Voice Chat Status**\n\n"
        f"🎵 **Now Playing:**\n"
        f"└ {active.get('title', 'Unknown')[:50]}\n"
        f"   ⏱ {active.get('duration', '?')} | 🎤 {active.get('channel', '?')[:25]}\n\n"
        f"📋 **Queue:** {len(queue)} song(s)\n"
        f"▶️ **Status:** {'⏸ Paused' if is_paused else '▶️ Playing'}\n"
        f"🔁 **Loop:** {loop_str}\n"
        f"🔊 **Volume:** {volume}%\n"
        f"🔄 **Autoplay:** {autoplay}"
    )
    await message.reply_text(text)


# ── Group join handler ────────────────────────────────────────────────────────

@Client.on_message(filters.new_chat_members)
async def new_member_handler(client: Client, message: Message):
    """Welcome message when bot is added to a group."""
    me = await client.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            await message.reply_text(
                f"👋 **Thanks for adding KanhaMusic!** 🎵\n\n"
                f"I can stream music in your Voice Chats from YouTube & Spotify.\n\n"
                f"**Quick Start:**\n"
                f"1️⃣ Start a Voice Chat in this group\n"
                f"2️⃣ Use `/play [song name]` — I'll join and play!\n\n"
                f"📋 Use `/help` to see all commands.\n"
                f"⚙️ Use `/settings` to configure the bot."
            )
            break
