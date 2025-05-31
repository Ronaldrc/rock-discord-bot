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
    get_all_streamer_status_db
)
from db.drop import (
    insert_drop_db,
    get_drop_sum_values_db,
    get_all_drop_sum_values_db
)
from db.death import (
    get_all_death_sum_values_db,
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
    get_all_streamer_status_db,
)
from db.profit_pk import (
    get_all_profit_pk_sum_values_db,
)
from db.bingo import (
    insert_bingo_drop_db
)
from config.logger_config import get_logger
from utils.utils import format_streamer_status_list, limit_message_length
from config.config import DiscordConfig
from webhooks.webhooks import (
    WebhookConfig,
    MessageCategory,
    getMessageCategory,
    sendContentToWebhook,
    extractRSN,
    extractDrop,
    extractLootValue,
    extractTimeInSeconds,
    checkForBingoDrop,
    extractBoss
)
from utils.utils import (
    datetime_to_discord_time_stamp
)

from rich import print

logger = get_logger(__name__)

### Get discord webhooks
webhook_config = WebhookConfig(".env")

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
STREAMERS_CHANNEL_ID = int(discord_config.STREAMERS_CHANNEL_ID)
STREAMERS_MESSAGE_ID = int(discord_config.STREAMERS_MESSAGE_ID)
GAME_CHAT_CHANNEL_ID = int(discord_config.GAME_CHAT_CHANNEL_ID)

@client.event
async def on_ready():
    await client.wait_until_ready()
    logger.info(f"Bot is ready and logged in as {client.user}")

    # channel = client.get_channel(discord_config.PROFIT_PK_1_HOUR_CHANNEL_ID)
    # await channel.send("hi")

    # channel = client.get_channel(discord_config.PROFIT_PK_3_HOUR_CHANNEL_ID)
    # await channel.send("hi")

    # channel = client.get_channel(discord_config.PROFIT_PK_6_HOUR_CHANNEL_ID)
    # await channel.send("hi")

    # channel = client.get_channel(discord_config.PROFIT_PK_12_HOUR_CHANNEL_ID)
    # await channel.send("hi")

    # channel = client.get_channel(discord_config.PROFIT_PK_1_DAY_CHANNEL_ID)
    # await channel.send("hi")

    # channel = client.get_channel(discord_config.PROFIT_PK_7_DAY_CHANNEL_ID)
    # await channel.send("hi")

    # channel = client.get_channel(discord_config.PROFIT_PK_30_DAY_CHANNEL_ID)
    # await channel.send("hi")

    refresh_token_periodically.start()
    pk_1_hour.start()
    pk_3_hour.start()
    pk_6_hour.start()
    pk_12_hour.start()
    pk_1_day.start()
    pk_7_day.start()
    pk_30_day.start()

    death_1_hour.start()
    death_3_hour.start()
    death_6_hour.start()
    death_12_hour.start()
    death_1_day.start()
    death_7_day.start()
    death_30_day.start()

    drop_1_hour.start()
    drop_3_hour.start()
    drop_6_hour.start()
    drop_12_hour.start()
    drop_1_day.start()
    drop_7_day.start()
    drop_30_day.start()

    profit_pk_1_hour.start()
    profit_pk_3_hour.start()
    profit_pk_6_hour.start()
    profit_pk_12_hour.start()
    profit_pk_1_day.start()
    profit_pk_7_day.start()
    profit_pk_30_day.start()

    edit_streamer_status_msg.start()
    check_kick_streams_periodically.start()
    check_twitch_streams_periodically.start()


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
        message: discord.Message
            Contains 

    """
    # send message to appropriate channel via webhook
    category = None
    content_dict = None
    if message.channel.id == GAME_CHAT_CHANNEL_ID:
        # <:TaskMastericon:1147705076677345322>ScytheMane has completed the Hard Kandarin diary\.
        #   Here, remove the prefix, <:TaskMastericon:1147705076677345322>
        no_emoji_message = message.content.replace('\\', '')
        emoji_end_index = message.content.find(">")
        if emoji_end_index:
            # no_emoji_message is
            #   ScytheMane has completed the Hard Kandarin diary.
            no_emoji_message = no_emoji_message[emoji_end_index + 1:]

            content_dict = getMessageCategory(no_emoji_message)

            if content_dict:
                webhook_url = content_dict.get('url', None)
                coded_message = content_dict.get('message', None)  # has new prefix emoji
                category = content_dict.get('category', None)
                
                # If valid category and webhook_url
                #   Some drops require the value to be added at the end
                if category != MessageCategory.DROP:
                    try:
                        await sendContentToWebhook(
                            webhook_url=webhook_url,
                            message=coded_message
                        )
                    except Exception as e:
                        logger.error(f"Failed to send content to webhook - {e}")

        # Send relevant information to database
        if category == MessageCategory.PK:
            # send to database
            no_emoji_message, loot_string = await extractLootValue(no_emoji_message, category)
            data = {
                "rsn": extractRSN(no_emoji_message, category),
                "loot_string": loot_string,
                "loot_big_int": int(loot_string)
            }
            await insert_player_kill_db(async_session, data)
        elif category == MessageCategory.DEATH:
            # send to database
            no_emoji_message, loot_string = await extractLootValue(no_emoji_message, category)
            data = {
                "rsn": extractRSN(no_emoji_message, category),
                "loot_string": loot_string,
                "loot_big_int": int(loot_string)
            }
            await insert_death_db(async_session, data)
        elif category == MessageCategory.PERSONAL_BEST:
            # send to database
            data = {
                "rsn": extractRSN(no_emoji_message, category),
                "boss": extractBoss(no_emoji_message, category),
                "duration": extractTimeInSeconds(no_emoji_message)
            }
            await insert_personal_best_db(async_session, data)
        elif category == MessageCategory.DROP:
            # send to database
            no_emoji_message, loot_string = await extractLootValue(no_emoji_message, category)
            data = {
                "rsn": extractRSN(no_emoji_message, category),
                "item": extractDrop(no_emoji_message, category),
                "loot_string": loot_string,
                "loot_big_int": int(loot_string)
            }
            await insert_drop_db(async_session, data)

            # Add prefix, value then send drop to webhook
            coded_message = f":moneybag:{no_emoji_message}"
            try:
                await sendContentToWebhook(
                    webhook_url=webhook_url,
                    message=coded_message
                )
            except Exception as e:
                logger.error(f"Failed to send content to webhook - {e}")

        # BINGO BINGO BINGO
        #   Check for bingo drop for drops
        #   Send bingo drops to appropriate channels
        #       change .env for appropriate bingo channel
        if content_dict:
            content_dict = checkForBingoDrop(no_emoji_message, content_dict)
            # FIXME: send to appropriate #bingo-drop discord webhook
            if content_dict.get("isBingo"):
                if content_dict["teamName"] == "blue":
                    coded_message = "🔵" + coded_message
                    bingo_webhook_url = webhook_config.BINGO_DROPS_URL
                elif content_dict["teamName"] == "green":
                    coded_message = "🟢" + coded_message
                    bingo_webhook_url = webhook_config.BINGO_DROPS_URL
                elif content_dict["teamName"] == "red":
                    coded_message = "🔴" + coded_message
                    bingo_webhook_url = webhook_config.BINGO_DROPS_URL

            if content_dict.get("teamName"):
                # Check if duplicate before sending
                #   query the item, rsn occured within 3 seconds prior
                try:
                    # send to bingo_drop database
                    data = {
                        "rsn": extractRSN(no_emoji_message, category),
                        "item": extractDrop(no_emoji_message, category),
                        "team_name": content_dict["teamName"],
                    }
                    await insert_bingo_drop_db(async_session, data)

                    # send to webhook
                    await sendContentToWebhook(
                        webhook_url=bingo_webhook_url,
                        message=coded_message
                    )
                except Exception as e:
                    logger.error(f"Failed to send content to webhook - {e}")


###################################################
#################### Send scheduled PK loot to webhooks
###################################################

async def update_pk_message(
    num_hours: int, 
    channel_id: int, 
    message_id: int
):
    max_char_per_message = 1900

    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    result = await get_all_pk_sum_values_db(
        async_session=async_session,
        time_range_hours=num_hours
    )

    if result is not None:
        formatted_string = "".join(
            f"{i+1}) {name:<15}{int(value):,}\n" for i, (name, value) in enumerate(result)
        )
    else:
        formatted_string = "No content!\n"
        
    # Limit message length to 1900 characters while ensuring it ends with a newline
    formatted_string = limit_message_length(formatted_string)
    formatted_string += f"{datetime_to_discord_time_stamp(datetime.now())}"

    # Edit the message with the safe length
    await message.edit(content=formatted_string)


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_1_hour():
    await update_pk_message(
        num_hours=1,
        channel_id=discord_config.PK_1_HOUR_CHANNEL_ID, 
        message_id=discord_config.PK_1_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_3_hour():
    await update_pk_message(
        num_hours=3,
        channel_id=discord_config.PK_3_HOUR_CHANNEL_ID, 
        message_id=discord_config.PK_3_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_6_hour():
    await update_pk_message(
        num_hours=6,
        channel_id=discord_config.PK_6_HOUR_CHANNEL_ID, 
        message_id=discord_config.PK_6_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_12_hour():
    await update_pk_message(
        num_hours=12,
        channel_id=discord_config.PK_12_HOUR_CHANNEL_ID, 
        message_id=discord_config.PK_12_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_1_day():
    await update_pk_message(
        num_hours=24,
        channel_id=discord_config.PK_1_DAY_CHANNEL_ID, 
        message_id=discord_config.PK_1_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_7_day():
    await update_pk_message(
        num_hours=24*7,
        channel_id=discord_config.PK_7_DAY_CHANNEL_ID, 
        message_id=discord_config.PK_7_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def pk_30_day():
    await update_pk_message(
        num_hours=24*30,
        channel_id=discord_config.PK_30_DAY_CHANNEL_ID, 
        message_id=discord_config.PK_30_DAY_MESSAGE_ID
    )


###################################################
#################### Send scheduled death to discord channel
###################################################

async def update_death_message(
    num_hours: int,
    channel_id: int, 
    message_id: int
):
    max_char_per_message = 1900

    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    result = await get_all_death_sum_values_db(
        async_session=async_session,
        time_range_hours=num_hours
    )

    if result is not None:
        formatted_string = "".join(
            f"{i+1}) {name:<15}{int(value):,}\n" for i, (name, value) in enumerate(result)
        )
    else:
        formatted_string = "No content!\n"
        
    # Limit message length to 1900 characters while ensuring it ends with a newline
    formatted_string = limit_message_length(formatted_string)
    formatted_string += f"{datetime_to_discord_time_stamp(datetime.now())}"

    # Edit the message with the safe length
    try:
        await message.edit(content=formatted_string)
    except Exception as e:
        logger.error(f"Failed to edit message - {e}")
    

@tasks.loop(seconds=300)  # every 5 minutes
async def death_1_hour():
    await update_death_message(
        num_hours=1,
        channel_id=discord_config.DEATH_1_HOUR_CHANNEL_ID,
        message_id=discord_config.DEATH_1_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def death_3_hour():
    await update_death_message(
        num_hours=3,
        channel_id=discord_config.DEATH_3_HOUR_CHANNEL_ID,
        message_id=discord_config.DEATH_3_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def death_6_hour():
    await update_death_message(
        num_hours=6,
        channel_id=discord_config.DEATH_6_HOUR_CHANNEL_ID,
        message_id=discord_config.DEATH_6_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def death_12_hour():
    await update_death_message(
        num_hours=12,
        channel_id=discord_config.DEATH_12_HOUR_CHANNEL_ID,
        message_id=discord_config.DEATH_12_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def death_1_day():
    await update_death_message(
        num_hours=24,
        channel_id=discord_config.DEATH_1_DAY_CHANNEL_ID,
        message_id=discord_config.DEATH_1_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def death_7_day():
    await update_death_message(
        num_hours=24*7,
        channel_id=discord_config.DEATH_7_DAY_CHANNEL_ID,
        message_id=discord_config.DEATH_7_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def death_30_day():
    await update_death_message(
        num_hours=24*30,
        channel_id=discord_config.DEATH_30_DAY_CHANNEL_ID,
        message_id=discord_config.DEATH_30_DAY_MESSAGE_ID
    )


###################################################
#################### Send scheduled drop to discord channel
###################################################
async def update_drop_message(
    num_hours: int,
    channel_id: int,
    message_id: int
):
    max_char_per_message = 1900

    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    result = await get_all_drop_sum_values_db(
        async_session=async_session,
        time_range_hours=num_hours
    )

    if result is not None:
        formatted_string = "".join(
            f"{i+1}) {name:<15}{int(value):,}\n" for i, (name, value) in enumerate(result)
        )
    else:
        formatted_string = "No content!\n"
        
    # Limit message length to 1900 characters while ensuring it ends with a newline
    formatted_string = limit_message_length(formatted_string)
    formatted_string += f"{datetime_to_discord_time_stamp(datetime.now())}"

    # Edit the message with the safe length
    try:
        await message.edit(content=formatted_string)
    except Exception as e:
        logger.error(f"Failed to edit message - {e}")
    

@tasks.loop(seconds=300)  # every 5 minutes
async def drop_1_hour():
    await update_drop_message(
        num_hours=1,
        channel_id=discord_config.DROP_1_HOUR_CHANNEL_ID,
        message_id=discord_config.DROP_1_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def drop_3_hour():
    await update_drop_message(
        num_hours=3,
        channel_id=discord_config.DROP_3_HOUR_CHANNEL_ID,
        message_id=discord_config.DROP_3_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def drop_6_hour():
    await update_drop_message(
        num_hours=6,
        channel_id=discord_config.DROP_6_HOUR_CHANNEL_ID,
        message_id=discord_config.DROP_6_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def drop_12_hour():
    await update_drop_message(
        num_hours=12,
        channel_id=discord_config.DROP_12_HOUR_CHANNEL_ID,
        message_id=discord_config.DROP_12_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def drop_1_day():
    await update_drop_message(
        num_hours=24,
        channel_id=discord_config.DROP_1_DAY_CHANNEL_ID,
        message_id=discord_config.DROP_1_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def drop_7_day():
    await update_drop_message(
        num_hours=24*7,
        channel_id=discord_config.DROP_7_DAY_CHANNEL_ID,
        message_id=discord_config.DROP_7_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def drop_30_day():
    await update_drop_message(
        num_hours=24*30,
        channel_id=discord_config.DROP_30_DAY_CHANNEL_ID,
        message_id=discord_config.DROP_30_DAY_MESSAGE_ID
    )


###################################################
#################### Send scheduled profit pk to discord channel
###################################################

async def update_profit_pk_message(
    num_hours: int,
    channel_id: int,
    message_id: int
):
    max_char_per_message = 1900

    channel = client.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    formatted_string = await get_all_profit_pk_sum_values_db(
        async_session=async_session,
        time_range_hours=num_hours
    )
        
    # Limit message length to 1900 characters while ensuring it ends with a newline
    formatted_string = limit_message_length(formatted_string)
    formatted_string += f"{datetime_to_discord_time_stamp(datetime.now())}"

    # Edit the message with the safe length
    try:
        await message.edit(content=formatted_string)
    except Exception as e:
        logger.error(f"Failed to edit message - {e}")


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_1_hour():
    await update_profit_pk_message(
        num_hours=1,
        channel_id=discord_config.PROFIT_PK_1_HOUR_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_1_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_3_hour():
    await update_profit_pk_message(
        num_hours=3,
        channel_id=discord_config.PROFIT_PK_3_HOUR_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_3_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_6_hour():
    await update_profit_pk_message(
        num_hours=6,
        channel_id=discord_config.PROFIT_PK_6_HOUR_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_6_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_12_hour():
    await update_profit_pk_message(
        num_hours=12,
        channel_id=discord_config.PROFIT_PK_12_HOUR_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_12_HOUR_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_1_day():
    await update_profit_pk_message(
        num_hours=24,
        channel_id=discord_config.PROFIT_PK_1_DAY_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_1_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_7_day():
    await update_profit_pk_message(
        num_hours=24*7,
        channel_id=discord_config.PROFIT_PK_7_DAY_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_7_DAY_MESSAGE_ID
    )


@tasks.loop(seconds=300)  # every 5 minutes
async def profit_pk_30_day():
    await update_profit_pk_message(
        num_hours=24*30,
        channel_id=discord_config.PROFIT_PK_30_DAY_CHANNEL_ID,
        message_id=discord_config.PROFIT_PK_30_DAY_MESSAGE_ID
    )


###################################################
####################
###################################################

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
async def edit_streamer_status_msg():
    try:
        logger.info("Editing streamer live, not live msg")
        channel = client.get_channel(STREAMERS_CHANNEL_ID)
        message_to_edit = await channel.fetch_message(STREAMERS_MESSAGE_ID)
        live, not_live = await get_all_streamer_status_db(async_session)
        formatted_string = format_streamer_status_list(live, not_live)
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
