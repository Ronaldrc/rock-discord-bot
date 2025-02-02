import requests
from config.logger_config import get_logger
import asyncio
from urllib.parse import quote
from db.db_init import (
    async_session
)
from db.streamer import (
    add_or_update_streamer_db,
    get_is_live_status_db,
    get_twitch_profile_pic
)
from utils.utils import (
    create_embedding,
    send_live_notification,
    read_streamers
)
from config.config import TwitchConfig
from datetime import datetime, timezone
from discord.ext.commands import Bot

logger = get_logger(__name__)

twitch_config = TwitchConfig(".env")

TWITCH_REFRESH_TOKEN = twitch_config.TWITCH_REFRESH_TOKEN
TWITCH_CLIENT_ID = twitch_config.TWITCH_CLIENT_ID
TWITCH_CLIENT_SECRET = twitch_config.TWITCH_CLIENT_SECRET
TWITCH_ACCESS_TOKEN = twitch_config.TWITCH_ACCESS_TOKEN  # updated later

# url encode the refresh token
encoded_refresh_token = quote(TWITCH_REFRESH_TOKEN)


async def update_user_access_token():
    """
    Twitch suggests updating the user access token every hour.
    """
    global TWITCH_ACCESS_TOKEN
    try:
        logger.info("Updating twitch user access token")
        url = 'https://id.twitch.tv/oauth2/token'
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": encoded_refresh_token,
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET
        }
        r = requests.post(url, data=payload)
        data = r.json()
        TWITCH_ACCESS_TOKEN = data['access_token']
    except Exception as e:
        logger.error(f"Failed to refresh user access token - {e}")

async def update_twitch_profile_pic(streamer: str):
    """
    Update one twitch user's profile picture and username in database.

    For twitch streams, profile pictures and usernames are added to database before
    their online status is checked.
    """
    try:
        logger.info("Updating a Twitch profile picture")
        url = 'https://api.twitch.tv/helix/users'
        headers = {
            "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
            "Client-Id": TWITCH_CLIENT_ID
        }
        params = {
            "login": streamer
        }
        r = requests.get(url, params=params, headers=headers)
        data = r.json()['data']

        parsed_data = {
            "name": (data[0].get('display_name') if data else "N/A"),
            "profile_pic": (
                data[0].get('profile_image_url', "N/A")
                if data else "N/A"
            ),
            "url": f"https://twitch.tv/{streamer}"
        }

        # Twitch name exists
        if parsed_data['name'] != "N/A":
            await add_or_update_streamer_db(async_session, parsed_data)
    except Exception as e:
        logger.error(f"Failed to get one twitch profile picture - {e}")

async def update_all_twitch_profile_pics(streamers: list[str]):
    """
    For twitch streams, profile pictures and usernames are added to database before
    their online status is checked.
    """
    logger.info("Updating all Twitch profile pictures")
    tasks = []
    for streamer in streamers:
        tasks.append(asyncio.create_task(
            update_twitch_profile_pic(
                streamer=streamer,
            )
        )
    )
    await asyncio.gather(*tasks)

async def get_twitch_stream_status(client: Bot, streamer: str):
    try:
        logger.info("Getting a Twitch stream status")
        url = 'https://api.twitch.tv/helix/streams'
        headers = {
            "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
            "Client-Id": TWITCH_CLIENT_ID
        }
        params = {
            "user_login": streamer
        }
        r = requests.get(url, params=params, headers=headers)
        data = r.json()['data']

        video_thumbnail = (
            data[0].get("thumbnail_url", "N/A")
            if data else "N/A"
        )
        parsed_data = {
            "name": streamer,
            "title": (data[0].get('title', "N/A") if data else "N/A"),
            "is_live": (True if data else False),
            "stream_id": (data[0].get('stream_id', -1) if data else -1),
            "video_thumbnail": (
                video_thumbnail.format(width=1920, height=1080)
                if video_thumbnail != "N/A" else "N/A"
            ),
            "url": f"https://twitch.tv/{streamer}"
        }

        # Profile picture not in data - obtain from db
        parsed_data["profile_pic"] = await get_twitch_profile_pic(
            async_session,
            parsed_data
        )

        was_is_live = await get_is_live_status_db(
            async_session,
            parsed_data
        )
        current_is_live = parsed_data['is_live']

        # send embedding to channel
        if not was_is_live and current_is_live:
            embed = create_embedding(parsed_data, "Twitch")
            parsed_data['start_time'] = datetime.now(timezone.utc)
            await send_live_notification(client, embed)
            await add_or_update_streamer_db(async_session, parsed_data)
        elif was_is_live and not current_is_live:
            parsed_data['start_time'] = datetime.now(timezone.utc)
            await add_or_update_streamer_db(async_session, parsed_data)

    except Exception as e:
        logger.error(f"Failed to get a twitch user status - {e}")


async def get_all_twitch_stream_status(client: Bot, streamers: list[str]):
    await update_all_twitch_profile_pics(streamers)  # do before
    logger.info("Getting all Twitch streams statuses")

    tasks = []
    for streamer in streamers:
        tasks.append(asyncio.create_task(
            get_twitch_stream_status(
                client=client,
                streamer=streamer
            )
        )
    )
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    # token = asyncio.run(update_user_access_token())
    file_name = "input/twitch_streamers.txt"
    twitch_streamers = read_streamers(file_name)
    # asyncio.run(get_twitch_users(file_name))
    asyncio.run(update_all_twitch_profile_pics(twitch_streamers))
    # asyncio.run(get_all_twitch_stream_status(twitch_streamers))
