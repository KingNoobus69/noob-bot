import discord
from discord import app_commands
from discord.ext import commands
from clash_api import get_player_data, get_clan_data, normalise_tag

from config import DISCORD_TOKEN, GUILD_ID, CLAN_TAG
from database import (
    init_db,
    insert_link,
    update_link,
    get_tag,
    get_discord_user_by_tag,
    delete_link,
    get_all_links,
    get_all_links_by_tag
)
from clash_api import get_player_data, get_clan_members, normalise_tag


REGISTER_ALLOWED_ROLES = {"Developer", "S.B Leader", "TempAdmin", "Moderator"}
LIST_ALLOWED_ROLES = {"Developer", "S.B Leader", "TempAdmin", "Moderator"}
UNLINK_ALLOWED_ROLES = {"Developer", "S.B Leader", "TempAdmin", "Moderator"}
UPDATE_ALLOWED_ROLES = {"Developer", "S.B Leader", "TempAdmin", "Moderator"}
PLAYER_DB_ALLOWED_ROLES = {"Developer", "S.B Leader", "TempAdmin", "Moderator"}


def user_has_allowed_role(interaction: discord.Interaction, allowed_roles: set[str]) -> bool:
    if not isinstance(interaction.user, discord.Member):
        return False

    user_role_names = {role.name for role in interaction.user.roles}
    return any(role in allowed_roles for role in user_role_names)


def register_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return user_has_allowed_role(interaction, REGISTER_ALLOWED_ROLES)
    return app_commands.check(predicate)


def list_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return user_has_allowed_role(interaction, LIST_ALLOWED_ROLES)
    return app_commands.check(predicate)


def unlink_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return user_has_allowed_role(interaction, UNLINK_ALLOWED_ROLES)
    return app_commands.check(predicate)


def update_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return user_has_allowed_role(interaction, UPDATE_ALLOWED_ROLES)
    return app_commands.check(predicate)


def player_db_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        return user_has_allowed_role(interaction, PLAYER_DB_ALLOWED_ROLES)
    return app_commands.check(predicate)


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def setup_hook():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)


bot.setup_hook = setup_hook


@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="register", description="Link a Discord member to a Clash Royale tag")
@app_commands.describe(user="Discord member", tag="Clash Royale player tag")
@register_only()
async def register(interaction: discord.Interaction, user: discord.Member, tag: str):
    clean_tag = normalise_tag(tag)

    existing_user_tag = get_tag(user.id)
    if existing_user_tag:
        await interaction.response.send_message(
            f"{user.mention} is already linked to `{existing_user_tag}`. Use `/update` instead.",
            ephemeral=True
        )
        return

    existing_tag_owner = get_discord_user_by_tag(clean_tag)
    if existing_tag_owner:
        await interaction.response.send_message(
            f"The tag `{clean_tag}` is already linked to another Discord user.",
            ephemeral=True
        )
        return

    try:
        insert_link(user.id, clean_tag, interaction.user.id)
        await interaction.response.send_message(
            f"Linked {user.mention} to `{clean_tag}`.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Failed to register player: {e}",
            ephemeral=True
        )


@bot.tree.command(name="update", description="Update a linked Clash Royale tag for a Discord member")
@app_commands.describe(user="Discord member", tag="New Clash Royale player tag")
@update_only()
async def update(interaction: discord.Interaction, user: discord.Member, tag: str):
    clean_tag = normalise_tag(tag)

    existing_user_tag = get_tag(user.id)
    if not existing_user_tag:
        await interaction.response.send_message(
            f"{user.mention} is not linked yet. Use `/register` first.",
            ephemeral=True
        )
        return

    existing_tag_owner = get_discord_user_by_tag(clean_tag)
    if existing_tag_owner and str(existing_tag_owner) != str(user.id):
        await interaction.response.send_message(
            f"The tag `{clean_tag}` is already linked to another Discord user.",
            ephemeral=True
        )
        return

    if existing_user_tag == clean_tag:
        await interaction.response.send_message(
            f"{user.mention} is already linked to `{clean_tag}`.",
            ephemeral=True
        )
        return

    try:
        update_link(user.id, clean_tag, interaction.user.id)
        await interaction.response.send_message(
            f"Updated {user.mention} from `{existing_user_tag}` to `{clean_tag}`.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Failed to update player: {e}",
            ephemeral=True
        )


@bot.tree.command(name="player", description="Show Clash Royale stats for a linked Discord member")
@app_commands.describe(user="Discord member")
async def player(interaction: discord.Interaction, user: discord.Member):
    tag = get_tag(user.id)

    if not tag:
        await interaction.response.send_message(
            f"No Clash Royale tag is linked for {user.mention}.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    try:
        data = await get_player_data(tag)

        player_name = data.get("name", "Unknown")
        player_tag = data.get("tag", tag)
        trophies = data.get("trophies", "N/A")
        best_trophies = data.get("bestTrophies", "N/A")
        exp_level = data.get("expLevel", "N/A")
        wins = data.get("wins", "N/A")
        losses = data.get("losses", "N/A")
        clan_name = data.get("clan", {}).get("name", "No clan")
        clan_role = data.get("role", "Unknown")

        embed = discord.Embed(
            title=player_name,
            description=f"Tag: {player_tag}"
        )
        embed.add_field(name="Trophies", value=str(trophies), inline=True)
        embed.add_field(name="Best Trophies", value=str(best_trophies), inline=True)
        embed.add_field(name="King Level", value=str(exp_level), inline=True)
        embed.add_field(name="Clan", value=clan_name, inline=True)
        embed.add_field(name="Role", value=clan_role, inline=True)
        embed.add_field(name="Wins", value=str(wins), inline=True)
        embed.add_field(name="Losses", value=str(losses), inline=True)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(
            f"Failed to fetch player data: {e}",
            ephemeral=True
        )


@bot.tree.command(name="player_db", description="Show clan members and Discord link status")
@player_db_only()
async def player_db(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)

    try:
        clan_data = await get_clan_data(CLAN_TAG)
        clan_name = clan_data.get("name", "Unknown Clan")
        clan_tag = clan_data.get("tag", CLAN_TAG)
        clan_members = clan_data.get("memberList", [])

        link_rows = get_all_links_by_tag()
        link_map = {cr_tag: discord_user_id for cr_tag, discord_user_id in link_rows}

        linked_count = sum(1 for member in clan_members if member.get("tag") in link_map)

        # Fixed column widths
        NAME_WIDTH = 20
        TAG_WIDTH = 12
        LINKED_WIDTH = 6
        DISCORD_WIDTH = 20

        table_header = (
            f"`{'CR Name':<{NAME_WIDTH}} | "
            f"{'CR Tag':<{TAG_WIDTH}} | "
            f"{'Linked':<{LINKED_WIDTH}} | "
            f"{'Discord User':<{DISCORD_WIDTH}}`"
        )
        table_separator = (
            f"`{'-' * NAME_WIDTH}-+-"
            f"{'-' * TAG_WIDTH}-+-"
            f"{'-' * LINKED_WIDTH}-+-"
            f"{'-' * DISCORD_WIDTH}`"
        )

        rows = []
        for member in clan_members:
            name = member.get("name", "Unknown")[:NAME_WIDTH]
            tag = member.get("tag", "N/A")[:TAG_WIDTH]

            discord_user_id = link_map.get(tag)
            linked_text = "Yes" if discord_user_id else "No"

            if discord_user_id:
                member_obj = interaction.guild.get_member(int(discord_user_id))
                discord_text = f"@{member_obj.display_name}" if member_obj else "@Unknown User"
            else:
                discord_text = "-"

            discord_text = discord_text[:DISCORD_WIDTH]

            row = (
                f"`{name:<{NAME_WIDTH}} | "
                f"{tag:<{TAG_WIDTH}} | "
                f"{linked_text:<{LINKED_WIDTH}} | "
                f"{discord_text:<{DISCORD_WIDTH}}`"
            )
            rows.append(row)

        # Build pages safely under Discord's 2000-char limit
        pages = []
        current_rows = []

        base_top = [
            f"**{clan_name} ({clan_tag})**",
            "Current clan member Discord link overview",
            "",
            table_header,
            table_separator,
        ]

        for row in rows:
            tentative_rows = current_rows + [row]

            # Build a test message with worst-case footer/page header included
            test_message = "\n".join(
                [
                    f"**{clan_name} ({clan_tag})**",
                    "Current clan member Discord link overview",
                    "",
                    "**Page 99/99**",
                    table_header,
                    table_separator,
                    *tentative_rows,
                    "",
                    f"**Linked players:** {linked_count}/{len(clan_members)}",
                ]
            )

            if len(test_message) > 1900:
                pages.append(current_rows)
                current_rows = [row]
            else:
                current_rows = tentative_rows

        if current_rows:
            pages.append(current_rows)

        for index, page_rows in enumerate(pages, start=1):
            message = "\n".join(
                [
                    f"**{clan_name} ({clan_tag})**",
                    "Current clan member Discord link overview",
                    "",
                    f"**Page {index}/{len(pages)}**",
                    table_header,
                    table_separator,
                    *page_rows,
                    "",
                    f"**Linked players:** {linked_count}/{len(clan_members)}",
                ]
            )

            await interaction.followup.send(message, ephemeral=False)

    except Exception as e:
        await interaction.followup.send(
            f"Failed to build player database view: {e}",
            ephemeral=True
        )


@bot.tree.command(name="unlink", description="Remove a linked Clash Royale tag from a Discord member")
@app_commands.describe(user="Discord member")
@unlink_only()
async def unlink(interaction: discord.Interaction, user: discord.Member):
    existing_tag = get_tag(user.id)

    if not existing_tag:
        await interaction.response.send_message(
            f"{user.mention} does not have a saved Clash Royale tag.",
            ephemeral=True
        )
        return

    delete_link(user.id)
    await interaction.response.send_message(
        f"Removed the saved Clash Royale tag for {user.mention}.",
        ephemeral=True
    )


@bot.tree.command(name="listplayers", description="Show all registered Clash Royale player links")
@list_only()
async def listplayers(interaction: discord.Interaction):
    links = get_all_links()

    if not links:
        await interaction.response.send_message(
            "No players are currently registered.",
            ephemeral=True
        )
        return

    lines = []
    for discord_user_id, cr_tag, linked_by_discord_id, linked_at in links:
        lines.append(f"<@{discord_user_id}> - `{cr_tag}`")

    message = "\n".join(lines)

    if len(message) > 1900:
        chunks = [message[i:i + 1900] for i in range(0, len(message), 1900)]

        await interaction.response.send_message(
            f"Registered players:\n{chunks[0]}",
            ephemeral=True
        )

        for chunk in chunks[1:]:
            await interaction.followup.send(chunk, ephemeral=True)
    else:
        await interaction.response.send_message(
            f"Registered players:\n{message}",
            ephemeral=True
        )


@register.error
@update.error
@unlink.error
@listplayers.error
@player_db.error
async def admin_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.CheckFailure):
        if interaction.response.is_done():
            await interaction.followup.send(
                "You do not have permission to use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True
            )
    else:
        if interaction.response.is_done():
            await interaction.followup.send(
                f"An error occurred: {error}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"An error occurred: {error}",
                ephemeral=True
            )


bot.run(DISCORD_TOKEN)