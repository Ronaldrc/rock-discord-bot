# from discord import app_commands
import discord
from discord.ext import commands
from discord import app_commands
from db.streamer import get_all_streamer_name_db
from db.db_init import async_session
from typing import Literal
from discord.utils import get
from config.logger_config import get_logger
from db.streamer import (
    add_streamer_slash_command_db,
    delete_streamer_slash_command_db
)
from db.db_init import async_session
from config.config import DiscordConfig

logger = get_logger(__name__)

discord_config = DiscordConfig()

PERSONAL_GUILD_ID = int(discord_config.DISCORD_GUILD_ID_PERSONAL) # personal server
ROCK_GUILD_ID = int(discord_config.DISCORD_GUILD_ID_ROCK) # personal server
LIST_GUILD_IDS = [PERSONAL_GUILD_ID, ROCK_GUILD_ID]

personal_guild = discord.Object(id=PERSONAL_GUILD_ID)


class Greetings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None

    @app_commands.command(name="hello", description="Say hello (to yourself) for fun!")
    @app_commands.guilds(*LIST_GUILD_IDS)
    async def hello(self, interaction: discord.Interaction):
        """Says hello (to yourself)"""
        member = interaction.user.nick or interaction.user.name
        if member != self._last_member:
            await interaction.response.send_message(f"Hello {member}. The last member to use 'hello' was {self._last_member}", ephemeral=True)
        else:
            await interaction.response.send_message(f'Hello {member}... This feels familiar.', ephemeral=True)
        self._last_member = member


class Streamers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="getstreamerlist", description="Retrieve the list of all streamers currently being tracked")
    @app_commands.guilds(*LIST_GUILD_IDS)
    async def getstreamerlist(
        self,
        interaction: discord.Interaction
    ):
        """Retrieve list of all streamers currently being tracked"""
        await interaction.response.defer(ephemeral=True)

        streamer_list = sorted(await get_all_streamer_name_db(async_session), key=str.lower)
        if streamer_list:
            await interaction.followup.send(
                f"List of streamers being tracked\n"
                "-------------------------------\n"
                + "\n".join(streamer_list)
            )
        else:
            await interaction.followup.send(
                f"Failed to retrieve the streamer list - please try again later"
            )

    @app_commands.command(name="sync", description="Lil brozzer only - do not use")
    @app_commands.guilds(PERSONAL_GUILD_ID)
    async def sync(
        self,
        interaction: discord.Interaction, 
    ):
        """Sync all slash commands"""
        member_roles = interaction.user.roles
        mod_role = get(member_roles, name="MOD")
        if mod_role:
            try:
                guild = discord.Object(id=PERSONAL_GUILD_ID)
                synced = await self.bot.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} command(s) for PERSONAL_SERVER")

                guild = discord.Object(id=ROCK_GUILD_ID)
                synced = await self.bot.tree.sync(guild=guild)
                logger.info(f"Synced {len(synced)} command(s) for ROCK_SERVER")
            except Exception as e:
                logger.error(f"Failed to sync commands - {e}")
            await interaction.response.send_message(f"Welcome MOD {interaction.user.nick or interaction.user.name}! Slash commands have been synced", ephemeral=True)
        else:
            await interaction.response.send_message(f"Unauthorized user - unable to execute sync command", ephemeral=True)
            logger.info(f"Unauthorized user {interaction.user.nick or interaction.user.name} - unable to execute sync command")

    @app_commands.command(name="addstreamer", description="Mod only - Add a streamer to be tracked")
    @app_commands.guilds(*LIST_GUILD_IDS)
    async def addstreamer(
        self,
        interaction: discord.Interaction,
        platform: Literal["kick", "twitch"],
        name: str
    ):
        """Add a new streamer to #streamers"""
        await interaction.response.defer(ephemeral=True)

        member_roles = interaction.user.roles
        mod_role = get(member_roles, name="MOD")
        retired_role = get(member_roles, name="RETIRED")
        marshal_role = get(member_roles, name="MARSHAL")

        # if mod or retired or marshal
        if mod_role or retired_role or marshal_role:
            if platform not in ["kick", "twitch"]:
                await interaction.followup.send("Platform must be 'kick' or 'twitch'.")
                return

            # Send the new streamer to the database
            data = {
                "platform": platform,
                "name": name,
                "url" : f"https://kick.com/{name}" if platform == 'kick' else f"https://twitch.tv/{name}"
            }
            await add_streamer_slash_command_db(async_session, data)
            logger.info(f"{interaction.user.nick or interaction.user.name} - used the addstreamer command")
            await interaction.followup.send(f"Good work. Now tracking username: {name}\nFeel free to use /getstreamerlist to confirm")
        else:
            await interaction.followup.send(f"Unauthorized user - unable to execute command")
            logger.info(f"Unauthorized user {interaction.user.nick or interaction.user.name} - unable to execute addstreamer command")

    @app_commands.command(name="deletestreamer", description="Admin only - Delete a streamer to be tracked")
    @app_commands.guilds(PERSONAL_GUILD_ID)
    async def deletestreamer(
        self,
        interaction: discord.Interaction, 
        name: str
    ):
        """Delete a streamer from #streamers"""
        await interaction.response.defer(ephemeral=True)

        member_roles = interaction.user.roles
        admin_role = get(member_roles, name="ADMIN")
        if admin_role:
            await delete_streamer_slash_command_db(async_session, name)
            await interaction.followup.send(f"Good work. Deleted username: {name}\nFeel free to use /getstreamerlist to confirm")
        else:
            await interaction.followup.send(f"Unauthorized user - unable to execute command")
            logger.info(f"Unauthorized user {interaction.user.nick or interaction.user.name} - unable to execute deletestreamer command")

    # @app_commands.command(name="checkroles", description="Check roles of user", guild=discord.Object(id=GUILD_ID))
    # @app_commands.guilds(GUILD_ID)
    # async def checkroles(
    #     self,
    #     interaction: discord.Interaction, 
    # ):
    #     await interaction.response.send_message(f"My roles are: \n{interaction.user.roles}")
