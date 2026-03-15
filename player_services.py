from clash_api import get_clan_data, get_player_data, normalise_tag
from database import get_all_links_by_tag
from config import CLAN_TAG, ORANGE_CLAN_TAG


async def get_live_clan_maps():
    sb_data = await get_clan_data(CLAN_TAG)
    so_data = await get_clan_data(ORANGE_CLAN_TAG)

    sb_name = sb_data.get("name", "Swimming Banana")
    sb_tag = sb_data.get("tag", CLAN_TAG)
    sb_members = sb_data.get("memberList", [])

    so_name = so_data.get("name", "Swimming Orange")
    so_tag = so_data.get("tag", ORANGE_CLAN_TAG)
    so_members = so_data.get("memberList", [])

    sb_member_map = {
        normalise_tag(member.get("tag", "")): member.get("name", "Unknown")
        for member in sb_members
    }
    so_member_map = {
        normalise_tag(member.get("tag", "")): member.get("name", "Unknown")
        for member in so_members
    }

    return {
        "sb_name": sb_name,
        "sb_tag": sb_tag,
        "sb_member_map": sb_member_map,
        "so_name": so_name,
        "so_tag": so_tag,
        "so_member_map": so_member_map,
    }


async def classify_linked_players():
    clan_maps = await get_live_clan_maps()

    sb_name = clan_maps["sb_name"]
    sb_tag = clan_maps["sb_tag"]
    sb_member_map = clan_maps["sb_member_map"]

    so_name = clan_maps["so_name"]
    so_tag = clan_maps["so_tag"]
    so_member_map = clan_maps["so_member_map"]

    sb_tags = set(sb_member_map.keys())
    so_tags = set(so_member_map.keys())

    link_rows = get_all_links_by_tag()
    link_map = {normalise_tag(cr_tag): discord_user_id for cr_tag, discord_user_id in link_rows}

    sb_linked = []
    so_linked = []
    other_linked = []

    for cr_tag, discord_user_id in link_map.items():
        if cr_tag in sb_tags:
            player_name = sb_member_map.get(cr_tag, "Unknown")
            sb_linked.append((player_name, cr_tag, discord_user_id))
        elif cr_tag in so_tags:
            player_name = so_member_map.get(cr_tag, "Unknown")
            so_linked.append((player_name, cr_tag, discord_user_id))
        else:
            try:
                player_data = await get_player_data(cr_tag)
                player_name = player_data.get("name", "Unknown")
            except Exception:
                player_name = "Unknown"

            other_linked.append((player_name, cr_tag, discord_user_id))

    sb_linked.sort(key=lambda x: x[0].lower())
    so_linked.sort(key=lambda x: x[0].lower())
    other_linked.sort(key=lambda x: x[0].lower())

    return {
        "sb_name": sb_name,
        "sb_tag": sb_tag,
        "so_name": so_name,
        "so_tag": so_tag,
        "sb_linked": sb_linked,
        "so_linked": so_linked,
        "other_linked": other_linked,
    }
