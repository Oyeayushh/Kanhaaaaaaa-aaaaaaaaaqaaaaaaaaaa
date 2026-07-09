"""
Audio stream helpers — join/change group call with audio-only stream.
Uses KanhaCall wrapper (core/call.py).
"""

from KanhaMusic.core.call import kanhaCall


async def stream_audio(chat_id: int, url: str) -> bool:
    """Join a group voice chat and stream audio-only. Returns True on success."""
    return await kanhaCall.join_call(chat_id, url, video=False)


async def change_audio(chat_id: int, url: str) -> bool:
    """Switch current stream to a new audio URL. Returns True on success."""
    return await kanhaCall.change_stream(chat_id, url, video=False)
