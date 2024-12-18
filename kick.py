import asyncio
from playwright.async_api import async_playwright
from database import add_or_update_streamer_db, get_is_live_status_db, async_session
from utils import send_live_notification, create_embedding, read_streamers
from logger_config import get_logger
from datetime import datetime, timezone

logger = get_logger(__name__)

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

async def get_all_kick_stream_status(client, streamers):
    try:
        # Webscrape Kick's public API
        logger.info(f"Getting Kick streams statuses...")
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
    
if __name__ == '__main__':
    streamers = read_streamers("input/kick_streamers.txt")
    asyncio.run(get_all_kick_stream_status(streamers))