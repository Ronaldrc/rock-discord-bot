import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from kick import get_all_kick_stream_status, read_streamers
from twitch import get_all_twitch_stream_status, update_user_access_token
from database import get_live_and_offline_streamers_db
import asyncio
from logger_config import get_logger
from datetime import datetime
from utils import format_live_and_not_live_lists

logger = get_logger(__name__)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = commands.Bot(command_prefix='!',intents=intents)

# Get all api keys
load_dotenv(".env")

DISCORD_APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID")
DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_LIVE_CHANNEL_ID = os.environ.get("DISCORD_LIVE_CHANNEL_ID")

# FIXME: replace with production variables
DISCORD_STREAM_TEXT_CHANNEL_ID = os.environ.get("DISCORD_STREAM_TEXT_CHANNEL_ID")
DISCORD_STREAM_TEXT_MESSAGE_ID = os.environ.get("DISCORD_STREAM_TEXT_MESSAGE_ID")

# FIXME: uncomment code inside on_ready function
@client.event
async def on_ready():
    logger.info(f"Bot is ready and logged in as {client.user}") 
    await client.wait_until_ready()
    refresh_token_periodically.start()
    await asyncio.gather(
        check_kick_streams_periodically.start(),
        check_twitch_streams_periodically.start()
    )

@tasks.loop(seconds=3600) # every hour
async def refresh_token_periodically():
    try:
        await update_user_access_token()
    except Exception as e:
        logger.error(f"Error with refresh token periodically: {e}")

@tasks.loop(seconds=60) # every minute
async def check_kick_streams_periodically():
    kick_streamers = read_streamers("input/kick_streamers.txt")
    try:
        await get_all_kick_stream_status(client, kick_streamers)
    except Exception as e:
        logger.error(f"Error with Kick streams periodic check: {e}")

@tasks.loop(seconds=60) # every minute
async def check_twitch_streams_periodically():
    twitch_streamers = read_streamers("input/twitch_streamers.txt")
    try:
        await get_all_twitch_stream_status(client, twitch_streamers)
    except Exception as e:
        logger.error(f"Error with Twitch streams periodic check: {e}")

# @tasks.loop(seconds=60) # every minute
# async def edit_streamer_live_not_live_msg():
#     try:
#         logger.info("Editing streamer live, not live msg")
#         channel = client.get_channel(int(DISCORD_STREAM_TEXT_CHANNEL_ID))
#         message_to_edit = await channel.fetch_message(int(DISCORD_STREAMERS_MESSAGE_ID))
#         live, not_live = await get_live_and_offline_streamers_db()
#         formatted_string = format_live_and_not_live_lists(live, not_live, datetime.now())
#         await message_to_edit.edit(content=formatted_string, suppress=True)
#     except Exception as e:
#         logger.error(f"Failed to edit streamer live not live msg: {e}")

async def main():
    await client.start(DISCORD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

# client.run(DISCORD_TOKEN)
