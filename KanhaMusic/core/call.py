"""
KanhaMusic — core/call.py
VC streaming engine. Wraps PyTgCalls with clean methods for join, leave,
change stream, pause, resume, mute, unmute, volume.

Usage anywhere in the project:
    from KanhaMusic.core.call import kanhaCall
    await kanhaCall.join_call(chat_id, url)
    await kanhaCall.leave_call(chat_id)
"""

import logging

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped

from KanhaMusic.core.userbot import assistant

logger = logging.getLogger("KanhaMusic.Call")

# Raw PyTgCalls instance (kept for @call_py.on_stream_end() decorator in main.py)
call_py = PyTgCalls(assistant)


class KanhaCall:
    """
    High-level wrapper around PyTgCalls.
    All VC operations go through this class.
    """

    def __init__(self, pytgcalls: PyTgCalls):
        self._call = pytgcalls

    # ── Join ────────────────────────────────────────────────────────────────

    async def join_call(
        self,
        chat_id: int,
        url: str,
        video: bool = False,
    ) -> bool:
        """
        Join a group voice chat and start streaming.

        Args:
            chat_id: Telegram group/channel ID.
            url:     Direct stream URL (from yt-dlp or any source).
            video:   True for audio+video stream, False for audio-only.

        Returns:
            True on success, False on failure.
        """
        try:
            stream = AudioVideoPiped(url) if video else AudioPiped(url)
            await self._call.join_group_call(chat_id, stream, stream_type=None)
            logger.info(f"[Call] Joined VC in chat {chat_id} ({'video' if video else 'audio'})")
            return True
        except Exception as e:
            logger.error(f"[Call] join_call({chat_id}) error: {e}")
            return False

    # ── Change Stream ────────────────────────────────────────────────────────

    async def change_stream(
        self,
        chat_id: int,
        url: str,
        video: bool = False,
    ) -> bool:
        """
        Switch the current stream to a new URL (e.g., next song in queue).

        Args:
            chat_id: Telegram group/channel ID.
            url:     New direct stream URL.
            video:   True for video stream, False for audio-only.

        Returns:
            True on success, False on failure.
        """
        try:
            stream = AudioVideoPiped(url) if video else AudioPiped(url)
            await self._call.change_stream(chat_id, stream)
            logger.info(f"[Call] Stream changed in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] change_stream({chat_id}) error: {e}")
            return False

    # ── Leave ────────────────────────────────────────────────────────────────

    async def leave_call(self, chat_id: int) -> bool:
        """
        Leave the voice chat in a group.

        Returns:
            True on success, False on failure.
        """
        try:
            await self._call.leave_group_call(chat_id)
            logger.info(f"[Call] Left VC in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] leave_call({chat_id}) error: {e}")
            return False

    # ── Pause / Resume ───────────────────────────────────────────────────────

    async def pause_call(self, chat_id: int) -> bool:
        """Pause the current stream."""
        try:
            await self._call.pause_stream(chat_id)
            logger.info(f"[Call] Paused in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] pause_call({chat_id}) error: {e}")
            return False

    async def resume_call(self, chat_id: int) -> bool:
        """Resume a paused stream."""
        try:
            await self._call.resume_stream(chat_id)
            logger.info(f"[Call] Resumed in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] resume_call({chat_id}) error: {e}")
            return False

    # ── Mute / Unmute ────────────────────────────────────────────────────────

    async def mute_call(self, chat_id: int) -> bool:
        """Mute the assistant in voice chat."""
        try:
            await self._call.mute_stream(chat_id)
            logger.info(f"[Call] Muted in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] mute_call({chat_id}) error: {e}")
            return False

    async def unmute_call(self, chat_id: int) -> bool:
        """Unmute the assistant in voice chat."""
        try:
            await self._call.unmute_stream(chat_id)
            logger.info(f"[Call] Unmuted in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] unmute_call({chat_id}) error: {e}")
            return False

    # ── Volume ───────────────────────────────────────────────────────────────

    async def volume_call(self, chat_id: int, volume: int) -> bool:
        """
        Change stream volume.

        Args:
            chat_id: Telegram group/channel ID.
            volume:  Volume level (1–200).

        Returns:
            True on success, False on failure.
        """
        try:
            await self._call.change_volume_call(chat_id, volume)
            logger.info(f"[Call] Volume set to {volume}% in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"[Call] volume_call({chat_id}) error: {e}")
            return False

    # ── Raw access ───────────────────────────────────────────────────────────

    @property
    def pytgcalls(self) -> PyTgCalls:
        """Direct access to the underlying PyTgCalls instance (for decorators)."""
        return self._call


# ── Singleton ────────────────────────────────────────────────────────────────
# Import this everywhere instead of using call_py directly:
#   from KanhaMusic.core.call import kanhaCall
kanhaCall = KanhaCall(call_py)
