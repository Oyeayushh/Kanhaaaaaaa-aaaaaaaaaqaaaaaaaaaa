"""
Autoplay utility for KanhaMusic.
Finds a related/similar song to play after the current one ends.

Strategy:
  1. Primary  — YouTube search by "artist name mix" / "songs like [title]"
  2. Fallback — search by artist name only
  3. Picks a random result from top-5 that isn't the same video
"""

import asyncio
import random
from typing import Optional

from KanhaMusic.utils.youtube import search_youtube, get_youtube_info


# Phrases that help YouTube surface related content
_SEED_TEMPLATES = [
    "{artist} best songs",
    "{artist} top hits",
    "{title} type beat",
    "songs like {title}",
    "{artist} mix",
    "{artist} playlist",
    "{title} similar songs",
]


async def get_related_track(
    title: str,
    artist: str,
    current_url: str = "",
    limit: int = 8,
) -> Optional[dict]:
    """
    Return info dict for a song related to the given title/artist.
    Tries multiple search strategies and picks a random top result
    that is different from the currently playing song.
    """
    # Build candidate queries
    queries = []
    clean_title = title.split("(")[0].split("[")[0].strip()[:50]
    clean_artist = artist.strip()[:40] if artist and artist != "Unknown" else ""

    for tmpl in _SEED_TEMPLATES:
        q = tmpl.format(title=clean_title, artist=clean_artist).strip()
        if q not in queries:
            queries.append(q)

    # Try each query until we find a good candidate
    for query in queries:
        try:
            results = await search_youtube(query, limit=limit)
            if not results:
                continue

            # Filter out the currently playing track
            candidates = [
                r for r in results
                if r.get("url") != current_url and r.get("title") != title
            ]
            if not candidates:
                candidates = results  # fallback: allow any

            # Pick randomly from top 5 to add variety
            pick = random.choice(candidates[:5])

            # Fetch full info for the chosen track
            info = await get_youtube_info(pick["url"])
            if info:
                return info

        except Exception as e:
            print(f"[Autoplay] Query '{query}' error: {e}")
            continue

    return None
