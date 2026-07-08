"""
Thumbnail generator for KanhaMusic.
Overlays song info on the brand thumbnail image.
"""

import asyncio
import os
import textwrap
from typing import Optional

import aiohttp

THUMB_DIR = "cache/thumbs"
BRAND_THUMB_URL = "https://h.uguu.se/PEdxUfYu.jpg"
BRAND_THUMB_LOCAL = "assets/thumbnail.jpg"

os.makedirs(THUMB_DIR, exist_ok=True)
os.makedirs("assets", exist_ok=True)


async def _download_image(url: str, dest: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    with open(dest, "wb") as f:
                        f.write(content)
                    return True
    except Exception as e:
        print(f"Image download error: {e}")
    return False


async def ensure_brand_thumb():
    """Download brand thumbnail if not cached locally."""
    if not os.path.exists(BRAND_THUMB_LOCAL):
        await _download_image(BRAND_THUMB_URL, BRAND_THUMB_LOCAL)


def _generate_thumb_sync(
    song_title: str,
    artist: str,
    duration: str,
    requested_by: str,
    song_thumb_url: Optional[str],
    output_path: str,
) -> str:
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import io
        import requests

        # Load brand base image
        if os.path.exists(BRAND_THUMB_LOCAL):
            base = Image.open(BRAND_THUMB_LOCAL).convert("RGBA")
        else:
            base = Image.new("RGBA", (1280, 720), (15, 10, 40, 255))

        base = base.resize((1280, 720))

        # Overlay dark gradient for readability
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)
        for i in range(720):
            alpha = int(180 * (i / 720))
            draw_ov.line([(0, i), (1280, i)], fill=(0, 0, 0, alpha))
        base = Image.alpha_composite(base, overlay)

        # Paste song thumbnail on right side if available
        if song_thumb_url:
            try:
                resp = requests.get(song_thumb_url, timeout=5)
                song_thumb = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                song_thumb = song_thumb.resize((380, 280))
                # Rounded mask
                mask = Image.new("L", song_thumb.size, 0)
                from PIL import ImageDraw as ID
                md = ID.Draw(mask)
                md.rounded_rectangle([0, 0, 380, 280], radius=20, fill=255)
                song_thumb.putalpha(mask)
                base.paste(song_thumb, (860, 220), song_thumb)
            except Exception:
                pass

        draw = ImageDraw.Draw(base)

        # Try to load fonts, fallback to default
        try:
            font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
        except Exception:
            font_big = ImageFont.load_default()
            font_med = font_big
            font_sm = font_big

        # Brand label
        draw.text((60, 40), "🎵 KanhaMusic", fill=(255, 215, 0), font=font_med)

        # Song title (wrap long titles)
        wrapped = textwrap.fill(song_title[:60], width=28)
        draw.text((60, 160), wrapped, fill=(255, 255, 255), font=font_big)

        # Artist
        draw.text((60, 340), f"🎤 {artist[:40]}", fill=(200, 200, 255), font=font_med)

        # Duration
        draw.text((60, 400), f"⏱ Duration: {duration}", fill=(180, 180, 180), font=font_sm)

        # Requested by
        draw.text((60, 450), f"👤 Requested by: {requested_by[:30]}", fill=(180, 220, 255), font=font_sm)

        # Bottom decorative bar
        draw.rectangle([(0, 690), (1280, 720)], fill=(255, 215, 0, 200))
        draw.text((480, 694), "✨ Powered by KanhaMusic ✨", fill=(0, 0, 0), font=font_sm)

        # Save
        rgb = base.convert("RGB")
        rgb.save(output_path, "JPEG", quality=95)
        return output_path

    except Exception as e:
        print(f"Thumbnail generation error: {e}")
        return BRAND_THUMB_LOCAL if os.path.exists(BRAND_THUMB_LOCAL) else ""


async def get_thumb(
    song_title: str,
    artist: str,
    duration: str,
    requested_by: str,
    song_thumb_url: Optional[str] = None,
    video_id: str = "",
) -> str:
    """
    Generate and return path to a thumbnail image for the currently playing song.
    Overlays song info on the KanhaMusic brand image.
    """
    await ensure_brand_thumb()

    output_path = f"{THUMB_DIR}/{video_id or abs(hash(song_title))}.jpg"

    if os.path.exists(output_path):
        return output_path

    result = await asyncio.get_event_loop().run_in_executor(
        None,
        _generate_thumb_sync,
        song_title,
        artist,
        duration,
        requested_by,
        song_thumb_url,
        output_path,
    )
    return result
