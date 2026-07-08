"""
Autoplay plugin for KanhaMusic.
Commands: /autoplay on | off | status
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from KanhaMusic.database import db
from KanhaMusic.utils.decorators import admin_or_auth, check_blacklist


def is_autoplay_on(chat_id: int) -> bool:
    return db.get_settings(chat_id).get("autoplay", False)


def set_autoplay(chat_id: int, state: bool):
    db.update_setting(chat_id, "autoplay", state)


def _autoplay_keyboard(chat_id: int, state: bool) -> InlineKeyboardMarkup:
    label_on  = "✅ ON"  if state else "▫️ ON"
    label_off = "▫️ OFF" if state else "✅ OFF"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(label_on,  callback_data=f"ap_on_{chat_id}"),
        InlineKeyboardButton(label_off, callback_data=f"ap_off_{chat_id}"),
    ]])


@Client.on_message(filters.command(["autoplay", "ap"]) & filters.group)
@check_blacklist
@admin_or_auth
async def autoplay_command(client: Client, message: Message):
    chat_id = message.chat.id
    args = message.command[1:]

    # Toggle or check with inline button if no arg given
    if not args:
        state = is_autoplay_on(chat_id)
        status = "🟢 **ON**" if state else "🔴 **OFF**"
        await message.reply_text(
            f"🔄 **Autoplay** is currently {status}\n\n"
            f"When enabled, KanhaMusic automatically plays a similar song "
            f"after each track ends.\n\n"
            f"Use the buttons below or `/autoplay on` / `/autoplay off`:",
            reply_markup=_autoplay_keyboard(chat_id, state),
        )
        return

    arg = args[0].lower()
    if arg in ("on", "enable", "1", "true"):
        set_autoplay(chat_id, True)
        await message.reply_text(
            "🔄 **Autoplay Enabled!** ✅\n\n"
            "KanhaMusic will automatically play a similar song when the current one ends.\n"
            "Use `/autoplay off` to disable.",
            reply_markup=_autoplay_keyboard(chat_id, True),
        )
    elif arg in ("off", "disable", "0", "false"):
        set_autoplay(chat_id, False)
        await message.reply_text(
            "🔄 **Autoplay Disabled** ❌\n\n"
            "Music will stop after the current song ends.\n"
            "Use `/autoplay on` to enable.",
            reply_markup=_autoplay_keyboard(chat_id, False),
        )
    else:
        await message.reply_text(
            "❌ Invalid option.\n\n"
            "**Usage:**\n"
            "`/autoplay on` — Enable autoplay\n"
            "`/autoplay off` — Disable autoplay\n"
            "`/autoplay` — Check status"
        )


@Client.on_callback_query(filters.regex(r"^ap_(on|off)_(-?\d+)$"))
async def autoplay_callback(client: Client, query: CallbackQuery):
    action  = query.matches[0].group(1)
    chat_id = int(query.matches[0].group(2))
    state   = (action == "on")

    set_autoplay(chat_id, state)
    status = "🟢 **ON**" if state else "🔴 **OFF**"

    await query.message.edit_text(
        f"🔄 **Autoplay** is now {status}\n\n"
        f"{'KanhaMusic will automatically play a similar song when the current one ends.' if state else 'Music will stop after the current song ends.'}\n\n"
        f"Use the buttons below or `/autoplay on` / `/autoplay off`:",
        reply_markup=_autoplay_keyboard(chat_id, state),
    )
    await query.answer(f"Autoplay {'enabled ✅' if state else 'disabled ❌'}")
