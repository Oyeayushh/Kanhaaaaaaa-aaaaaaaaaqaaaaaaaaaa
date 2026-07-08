"""
Audio stream helpers — join/change group call with audio-only stream.
Uses pytgcalls v0.9.x API (AudioPiped).
"""

from pytgcalls.types.input_stream import AudioPiped

from KanhaMusic.core.call import call_py


async def stream_audio(chat_id: int, url: str) -> bool:
    """Join a group voice chat and stream audio. Returns True on success."""
    try:
        await call_py.join_group_call(chat_id, AudioPiped(url), stream_type=None)
        return True
    except Exception as e:
        from KanhaMusic import logger
        logger.error(f"[stream_audio] chat={chat_id} error={e}")
        return False


async def change_audio(chat_id: int, url: str) -> bool:
    """Change the current stream to a new audio URL. Returns True on success."""
    try:
        await call_py.change_stream(chat_id, AudioPiped(url))
        return True
    except Exception as e:
        from KanhaMusic import logger
        logger.error(f"[change_audio] chat={chat_id} error={e}")
        return False
