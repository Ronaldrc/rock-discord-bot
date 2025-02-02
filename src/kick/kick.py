import asyncio
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
from config.logger_config import get_logger
from datetime import datetime, timezone
from discord.ext.commands import Bot
from rich import print

logger = get_logger(__name__)

def parse_json(data):
    user = data.get("user", {})
    livestream = data.get("livestream", {})
    thumbnail = livestream.get("thumbnail", {})
    parsed_json = {
        "name": user.get("username") if user else "N/A",
        "title": livestream.get("session_title", "N/A") if livestream else "N/A",
        "is_live": livestream.get("is_live", False)  if livestream else False,
        "stream_id": livestream.get("id", -1) if livestream else -1,
        "video_thumbnail": thumbnail.get("url", "N/A") if thumbnail else "N/A",
        "profile_pic": user.get("profile_pic", "N/A"),
        "url": f"https://kick.com/{user.get('username')}"
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


async def get_all_kick_stream_status(client: Bot, streamers: list[str]):
    """
    Webscrape Kick's backend API for streamer information

    Parameters
    ---------
    client: discord.ext.commands.Bot
        Discord bot instance, used to send embedding to discord channel.
    
    streamers: list[str]
        List of Kick streamers (case-insensitive)

    """
    logger.info("Getting all Kick streams statuses...")
    async with async_playwright() as p:
        tasks = []
        for streamer in streamers:
            tasks.append(asyncio.create_task(get_kick_stream_status(
                    client=client,
                    playwright=p,
                    streamer=streamer
                )
            )
        )
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    streamers = read_streamers("input/kick_streamers.txt")
    asyncio.run(get_all_kick_stream_status(streamers))
