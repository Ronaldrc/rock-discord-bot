import asyncio
import requests
from playwright.async_api import async_playwright, Playwright
from db.db_init import (
    async_session
)
from db.streamer import (
    add_or_update_streamer_db,
    get_is_live_status_db,
)
from utils.utils import (
    send_live_notification,
    create_embedding,
    read_streamers
)
from config.config import KickConfig
from urllib.parse import quote
from config.logger_config import get_logger
from datetime import datetime, timezone
from discord.ext.commands import Bot

logger = get_logger(__name__)

############### KICK API IS BROKEN - 31May2025: the wrong profile picture url was provided from the API
############### FIXME CODE BELOW FOR KICK

kick_config = KickConfig()

KICK_REFRESH_TOKEN = kick_config.KICK_REFRESH_TOKEN
KICK_CLIENT_ID = kick_config.KICK_CLIENT_ID
KICK_CLIENT_SECRET = kick_config.KICK_CLIENT_SECRET
KICK_ACCESS_TOKEN = kick_config.KICK_ACCESS_TOKEN  # updated later

# url encode the refresh token
encoded_refresh_token = quote(KICK_REFRESH_TOKEN)

# call every hour - update user access token
async def update_user_access_token():
    """
    Kick:
    Decided to update the user access token every hour, same with Twitch access token.
    """
    global KICK_ACCESS_TOKEN
    try:
        logger.info("Updating kick user access token")
        url = 'https://id.kick.com/oauth/token'
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": encoded_refresh_token,
            "client_id": KICK_CLIENT_ID,
            "client_secret": KICK_CLIENT_SECRET
        }
        r = requests.post(url, data=payload)
        data = r.json()
        KICK_ACCESS_TOKEN = data['access_token']
    except Exception as e:
        logger.error(f"Failed to refresh kick user access token - {e}")


############### FIX CODE ABOVE FOR KICK
############### FIX CODE ABOVE FOR KICK
############### FIX CODE ABOVE FOR KICK


def parse_json(data):
    parsed_json = {
        "name": data.get("user", {}).get("username"),
        "title": data.get("livestream", {}).get("session_title") if data.get("livestream") else "N/A",
        "is_live": data.get("livestream", {}).get("is_live") if data.get("livestream") else False,
        "stream_id": data.get("livestream", {}).get("id") if data.get("livestream") else -1,
        "video_thumbnail": data.get("livestream", {}).get("thumbnail", {}).get("url") if data.get("livestream") and data.get("livestream").get("thumbnail") else "N/A",
        "profile_pic": data.get("user", {}).get("profile_pic") if data.get("user") else "N/A",
        "url" : f"https://kick.com/{data.get("user", {}).get("username")}"
    }
    return parsed_json


async def get_kick_stream_status(client: Bot, playwright: Playwright, streamer: str):
    """
    Webscrape Kick's backend API for information for one streamer

    Parameters
    ---------
    client: discord.ext.commands.Bot
        Discord bot instance, used to send embedding to discord channel.

    streamer: str
        The name of the Kick streamer (case-insensitive)
    """

    logger.info(f"Getting kick status for {streamer}")
    try:
        # Webscrape
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        url = f'https://kick.com/api/v2/channels/{streamer}/'
        r = await page.goto(url)
        data = await r.json()
        parsed_data = parse_json(data)    # only save important fields
        await browser.close()

        # Verify online/offline status of streamer
        was_is_live = await get_is_live_status_db(
                        async_session,
                        parsed_data
                    )
        current_is_live = parsed_data['is_live']

        # Send embedding to channel
        if not was_is_live and current_is_live:
            embed = create_embedding(parsed_data, "Kick")
            parsed_data['start_time'] = datetime.now(timezone.utc)
            await send_live_notification(client, embed)
        elif was_is_live and not current_is_live:
            parsed_data['start_time'] = datetime.now(timezone.utc)

        await add_or_update_streamer_db(async_session, parsed_data)
    except Exception as e:
        logger.error(f"Failed to retrieve status for {streamer}: {e}")


async def get_all_kick_stream_status(client, streamers):
    try:
        logger.info(f"Getting all Kick streams statuses...")
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        for name in streamers:
            url = f'https://kick.com/api/v2/channels/{name}/'
            r = await page.goto(url, wait_until="networkidle")    # wait until webpage is fully loaded
            data = await r.json()
            parsed_data = parse_json(data)    # only save important fields

            was_is_live = await get_is_live_status_db(async_session, parsed_data)
            current_is_live = parsed_data['is_live']

            # send embedding to channel
            if was_is_live == False and current_is_live == True:
                embed = create_embedding(parsed_data, "Kick")
                parsed_data['start_time'] = datetime.now(timezone.utc)
                await send_live_notification(client, embed)
            elif was_is_live == True and current_is_live == False:
                parsed_data['start_time'] = datetime.now(timezone.utc)

            await add_or_update_streamer_db(async_session, parsed_data)
    except Exception as e:
        logger.error(f"get_all_kick_stream_status failed: {e}")
    finally:
        await p.stop()


# FIXME: This function overloads CPU of Raspberry pi 4 
# async def get_all_kick_stream_status(client: Bot, streamers: list[str]):
#     """
#     Webscrape Kick's backend API for streamer information

#     Parameters
#     ---------
#     client: discord.ext.commands.Bot
#         Discord bot instance, used to send embedding to discord channel.
    
#     streamers: list[str]
#         List of Kick streamers (case-insensitive)

#     """
#     logger.info("Getting all Kick streams statuses...")
#     async with async_playwright() as p:
#         tasks = []
#         for streamer in streamers:
#             tasks.append(asyncio.create_task(get_kick_stream_status(
#                     client=client,
#                     playwright=p,
#                     streamer=streamer
#                 )
#             )
#         )
#         await asyncio.gather(*tasks)
    

if __name__ == '__main__':
    streamers = read_streamers("input/kick_streamers.txt")
    asyncio.run(get_all_kick_stream_status(streamers))