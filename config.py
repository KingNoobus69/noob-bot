import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CLASH_API_TOKEN = os.getenv("CLASH_API_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CLAN_TAG = os.getenv("CLAN_TAG")

if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_TOKEN in .env")

if not CLASH_API_TOKEN:
    raise ValueError("Missing CLASH_API_TOKEN in .env")

if not GUILD_ID:
    raise ValueError("Missing GUILD_ID in .env")

if not CLAN_TAG:
    raise ValueError("Missing CLAN_TAG in .env")