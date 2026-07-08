"""
Generate a Pyrogram String Session for the assistant account.
Run: python generate_session.py
"""

import asyncio
from pyrogram import Client


async def generate():
    print("=" * 55)
    print("   KanhaMusic — Assistant String Session Generator")
    print("=" * 55)
    print()
    print("You need a SEPARATE Telegram account for the assistant.")
    print("(Not your main account, not the bot account)")
    print()

    api_id = int(input("Enter your API ID: ").strip())
    api_hash = input("Enter your API Hash: ").strip()

    async with Client(
        name="KanhaAssistantSession",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True,
    ) as client:
        session = await client.export_session_string()
        print()
        print("=" * 55)
        print("✅ Your STRING_SESSION:")
        print()
        print(session)
        print()
        print("=" * 55)
        print("Add this as STRING_SESSION in your config/.env")
        print("=" * 55)


if __name__ == "__main__":
    asyncio.run(generate())
