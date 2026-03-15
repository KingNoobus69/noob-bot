import aiohttp
from urllib.parse import quote

from config import CLASH_API_TOKEN


BASE_URL = "https://api.clashroyale.com/v1"


def normalise_tag(tag: str) -> str:
    clean_tag = tag.strip().upper()

    if not clean_tag.startswith("#"):
        clean_tag = "#" + clean_tag

    return clean_tag


async def get_player_data(player_tag: str):
    encoded_tag = quote(player_tag, safe="")
    url = f"{BASE_URL}/players/{encoded_tag}"

    headers = {
    "Authorization": f"Bearer {CLASH_API_TOKEN}",
    "Cache-Control": "no-cache"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()

            error_text = await response.text()
            raise Exception(f"Clash Royale API returned {response.status}: {error_text}")


async def get_clan_members(clan_tag: str):
    encoded_tag = quote(clan_tag, safe="")
    url = f"{BASE_URL}/clans/{encoded_tag}"

    headers = {
        "Authorization": f"Bearer {CLASH_API_TOKEN}",
        "Cache-Control": "no-cache"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("memberList", [])

            error_text = await response.text()
            raise Exception(f"Clash Royale API returned {response.status}: {error_text}")

async def get_clan_data(clan_tag: str):
    encoded_tag = quote(clan_tag, safe="")
    url = f"{BASE_URL}/clans/{encoded_tag}"

    headers = {
        "Authorization": f"Bearer {CLASH_API_TOKEN}",
        "Cache-Control": "no-cache"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()

            error_text = await response.text()
            raise Exception(f"Clash Royale API returned {response.status}: {error_text}")

async def get_current_river_race(clan_tag: str):
    encoded_tag = quote(clan_tag, safe="")
    url = f"{BASE_URL}/clans/{encoded_tag}/currentriverrace"

    headers = {
    "Authorization": f"Bearer {CLASH_API_TOKEN}",
    "Cache-Control": "no-cache"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()

            error_text = await response.text()
            raise Exception(f"Clash Royale API returned {response.status}: {error_text}")