import asyncio
import discord
from datetime import datetime
from discord.ext import commands, tasks
from kick.kick import get_all_kick_stream_status, read_streamers
from twitch.twitch import (
    get_all_twitch_stream_status,
    update_user_access_token
)
from db.db_init import (
    async_session,
    create_tables
)
from db.streamer import (
    get_live_and_offline_streamers_db
)
from db.drop import (
    insert_drop_db,
    get_drop_sum_values_db,
    get_all_drop_sum_values_db
)
from db.death import (
    get_all_deaths_sum_values_db,
    insert_death_db
)
from db.pb import (
    get_all_personal_best_db,
    insert_personal_best_db
)
from db.pk import (
    get_all_pk_sum_values_db,
    get_sum_pk_db,
    insert_player_kill_db,
)
from db.streamer import (
    get_live_and_offline_streamers_db,
)
from config.logger_config import get_logger
from utils.utils import format_live_and_not_live_lists
from config.config import DiscordConfig
from webhooks.webhooks import (
    MessageCategory,
    getMessageCategory,
    sendContentToWebhook,
    extractRSN,
    extractDrop,
    extractLootValue,
    extractTimeInSeconds
)

from rich import print

logger = get_logger(__name__)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = commands.Bot(command_prefix='!', intents=intents)

# Get all api keys
discord_config = DiscordConfig(".env")

DISCORD_APPLICATION_ID = discord_config.DISCORD_APPLICATION_ID
DISCORD_PUBLIC_KEY = discord_config.DISCORD_PUBLIC_KEY
DISCORD_TOKEN = discord_config.DISCORD_TOKEN
LIVE_CHANNEL_ID = discord_config.LIVE_CHANNEL_ID
STREAMERS_CHANNEL_ID = discord_config.STREAMERS_CHANNEL_ID
STREAMERS_MESSAGE_ID = discord_config.STREAMERS_MESSAGE_ID
GAME_CHAT_CHANNEL_ID = int(discord_config.GAME_CHAT_CHANNEL_ID)


@client.event
async def on_ready():
    logger.info(f"Bot is ready and logged in as {client.user}")
    await client.wait_until_ready()
    # refresh_token_periodically.start()
    # await asyncio.gather(
    #     check_kick_streams_periodically.start(),
    #     check_twitch_streams_periodically.start()
    # )


@client.event
async def on_message(message: discord.Message):
    """
        Called every time a message is sent in the server.
        
        Send message to the correct channel using webhooks.
        
        Also, store relevant information in database.
            - clan pbs
                - personal-best
            - pks-total-gp
                - pks
            - drops-total-gp
                - drops
            - recent total gp
                - pk-1h
                - pk-3h
                - etc.
        
        Parameters
        --------------------
        message: str

    """
    
    # send message to appropriate channel via webhook
    category = None
    if message.channel.id == GAME_CHAT_CHANNEL_ID:
        # print(message.content)

        # <:TaskMastericon:1147705076677345322>ScytheMane has completed the Hard Kandarin diary.
        #   Remove the prefix, <:TaskMastericon:1147705076677345322>
        emoji_end_index = message.content.find(">")
        if emoji_end_index:
            # no_emoji_message is ScytheMane has completed the Hard Kandarin diary.
            no_emoji_message = message.content[emoji_end_index + 1:]
            no_emoji_message = no_emoji_message.replace('\\', '')

            # print(f"no_emoji_message is: {no_emoji_message}")

            content_dict = getMessageCategory(no_emoji_message)

            if content_dict:
                webhook_url = content_dict.get('url', None)
                coded_message = content_dict.get('message', None)  # has new prefix emoji
                category = content_dict.get('category', None)
                # print(f"coded_message is: {coded_message}")

                # If valid category and webhook_url is valid
                # try:
                #     await sendContentToWebhook(
                #         webhook_url=webhook_url,
                #         message=coded_message
                #     )
                # except Exception as e:
                #     logger.error(f"Failed to send content to webhook - {e}")

        # extract from no_emoji_message
        #   personal-best
        #   pks
        #   drops

        # Send relevant information to database
        if category == MessageCategory.PK:
            # send to database
            loot_string = extractLootValue(no_emoji_message, MessageCategory.PK)
            data = {
                "rsn": extractRSN(no_emoji_message, MessageCategory.PK),
                "loot_string": loot_string,
                "loot_big_int": int(loot_string)
            }
            await insert_player_kill_db(async_session, data)
        elif category == MessageCategory.DEATH:
            # send to database
            loot_string = extractLootValue(no_emoji_message, MessageCategory.DEATH)
            data = {
                "rsn": extractRSN(no_emoji_message, MessageCategory.DEATH),
                "loot_string": loot_string,
                "loot_big_int": int(loot_string)
            }
            await insert_death_db(async_session, data)
        elif category == MessageCategory.DROP:
            # send to database
            loot_string = extractLootValue(no_emoji_message, MessageCategory.DROP)
            data = {
                "rsn": extractRSN(no_emoji_message, MessageCategory.DROP),
                "item": extractDrop(no_emoji_message, MessageCategory.DROP),
                "loot_string": loot_string,
                "loot_big_int": int(loot_string)
            }
            await insert_drop_db(async_session, data)

            # value = await get_drop_sum_values_db(
            #     async_session,
            #     data
            # )

            # values = await get_all_drop_sum_values_db(async_session, 15)
            # if values:
            #     for value in values:
            #         rsn = value[0]
            #         sum = value[1]
            #         print(f"{rsn} has a total loot value of {sum}")

        elif category == MessageCategory.PERSONAL_BEST:
            # send to database
            data = {
                "rsn": extractRSN(no_emoji_message, MessageCategory.PERSONAL_BEST),
                "duration": extractTimeInSeconds(no_emoji_message)
            }
            await insert_personal_best_db(async_session, data)


@tasks.loop(seconds=3600)  # every hour
async def refresh_token_periodically():
    try:
        await update_user_access_token()
    except Exception as e:
        logger.error(f"Error with refresh token periodically: {e}")


@tasks.loop(seconds=60)  # every minute
async def check_kick_streams_periodically():
    kick_streamers = read_streamers("input/kick_streamers.txt")
    try:
        await get_all_kick_stream_status(client, kick_streamers)
    except Exception as e:
        logger.error(f"Error with Kick streams periodic check: {e}")


@tasks.loop(seconds=60)  # every minute
async def check_twitch_streams_periodically():
    twitch_streamers = read_streamers("input/twitch_streamers.txt")
    try:
        await get_all_twitch_stream_status(client, twitch_streamers)
    except Exception as e:
        logger.error(f"Error with Twitch streams periodic check: {e}")


@tasks.loop(seconds=60)  # every minute
async def edit_streamer_live_not_live_msg():
    try:
        logger.info("Editing streamer live, not live msg")
        channel = client.get_channel(int(STREAMERS_CHANNEL_ID))
        message_to_edit = await channel.fetch_message(int(STREAMERS_MESSAGE_ID))
        live, not_live = await get_live_and_offline_streamers_db(async_session)
        formatted_string = format_live_and_not_live_lists(live, not_live)
        await message_to_edit.edit(content=formatted_string, suppress=True)
    except Exception as e:
        logger.error(f"Failed to edit streamer live, not live msg: {e}")


async def initialize_db() -> None:
    """
    Create table if it does not exist

    Returns
    ------------
    None
    """
    await create_tables()


async def main():
    await initialize_db()
    await client.start(DISCORD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())

# client.run(DISCORD_TOKEN)
