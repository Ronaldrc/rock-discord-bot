import requests
from logger_config import get_logger
import asyncio
from urllib.parse import quote
from dotenv import load_dotenv
import os
from rich import print
from database import add_or_update_streamer_db, get_is_live_status_db, get_twitch_profile_pic, async_session
from utils import create_embedding, send_live_notification, read_streamers
from datetime import datetime, timezone

logger = get_logger(__name__)

load_dotenv()

TWITCH_REFRESH_TOKEN = os.environ.get("TWITCH_REFRESH_TOKEN")
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
TWITCH_ACCESS_TOKEN = 'g'  # updated by update_user_access_token

# url encode the refresh token
encoded_refresh_token = quote(TWITCH_REFRESH_TOKEN)

# call every hour - update user access token
async def update_user_access_token():
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

async def update_all_twitch_profile_pics(streamers : list):
    try:
        logger.info(f"Updating Twitch profile pictures")
        for name in streamers:
            url = f'https://api.twitch.tv/helix/users'
            headers = {
                "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
                "Client-Id": TWITCH_CLIENT_ID
            }
            params = {
                "login" : name
            }
            r = requests.get(url, params=params, headers=headers)
            data = r.json()['data']

            parsed_data = {
                "name": (data[0].get('display_name') if data else "N/A"),
                "profile_pic": (data[0].get('profile_image_url', "N/A") if data else {"N/A"}),
                "url" : f"https://twitch.tv/{name}"
            }

            # Twitch name exists
            if parsed_data['name'] != "N/A":
                await add_or_update_streamer_db(async_session, parsed_data)
    except Exception as e:
        logger.error(f"Failed to get twitch profile pictures - {e}")

async def get_all_twitch_stream_status(client, streamers):
    try:
        await update_all_twitch_profile_pics(streamers)     # must be done first in-case there were new twitch streamers added to list
        logger.info(f"Getting Twitch streams statuses")
        for name in streamers:
            url = f'https://api.twitch.tv/helix/streams'
            headers = {
                "Authorization": f"Bearer {TWITCH_ACCESS_TOKEN}",
                "Client-Id": TWITCH_CLIENT_ID
            }
            params = {
                "user_login" : name
            }
            r = requests.get(url, params=params, headers=headers)
            data = r.json()['data']

            video_thumbnail = (data[0].get("thumbnail_url", "N/A") if data else "N/A")
            parsed_data = {
                "name": (data[0].get('user_name') if data else "N/A"),
                "title": (data[0].get('title', "N/A") if data else "N/A"),
                "is_live": (True if data else False),
                "stream_id": (data[0].get('stream_id', -1) if data else -1),  # not used in twitch streams! default -1
                "video_thumbnail": (video_thumbnail.format(width=1920, height=1080) if video_thumbnail != "N/A" else "N/A"),
                "url" : f"https://twitch.tv/{name}"
            }

            # Profile picture does not exist in data - must obtain from database
            parsed_data["profile_pic"] = await get_twitch_profile_pic(async_session, parsed_data)

            was_is_live = await get_is_live_status_db(async_session, parsed_data)
            current_is_live = parsed_data['is_live']

            # send embedding to channel
            if was_is_live == False and current_is_live == True:
                embed = create_embedding(parsed_data, "Twitch")
                parsed_data['start_time'] = datetime.now(timezone.utc)
                await send_live_notification(client, embed)
            elif was_is_live == True and current_is_live == False:
                parsed_data['start_time'] = datetime.now(timezone.utc)

    except Exception as e:
        logger.error(f"Failed to get all twitch users - {e}")

if __name__ == '__main__':
    # token = asyncio.run(update_user_access_token())
    file_name = "input/twitch_streamers.txt"
    twitch_streamers = read_streamers(file_name)
    # asyncio.run(get_twitch_users(file_name))
    asyncio.run(update_all_twitch_profile_pics(twitch_streamers))
    # asyncio.run(get_all_twitch_stream_status(twitch_streamers))
