import discord
import json
from config.logger_config import get_logger
from datetime import datetime, timedelta, timezone
from config.config import DiscordConfig

logger = get_logger(__name__)

discord_config = DiscordConfig(".env")
DISCORD_LIVE_CHANNEL_ID = discord_config.LIVE_CHANNEL_ID


async def send_live_notification(
    client: discord.Client,
    notification: discord.Embed
):
    try:
        id_int = int(DISCORD_LIVE_CHANNEL_ID)
        channel = client.get_channel(id_int)
        logger.info(f"Sending live notification to channel: {channel.name}")
        await channel.send(embed=notification)
    except Exception as e:
        logger.error(f"Failed to send live notification to channel - {e}")


def create_embedding(
    data: json,
    streaming_platform: str
):
    streamer_name = data['name']
    logger.info(f"Creating embedding for {streamer_name}")
    if streaming_platform == "Kick":
        url = f"https://kick.com/{streamer_name}"
    else:
        url = f"https://twitch.tv/{streamer_name}"
    
    embed = discord.Embed(
            title=f"{streamer_name} is live on {streaming_platform}!",
            type="rich",
            url=url,
            color=(5766193 if streaming_platform == "Kick" else 11104511)   # bright green for Kick, purple for Twitch
        )
    embed.add_field(name=f"{data['title']}", value="")
    embed.set_image(url=f"{data['video_thumbnail']}")  # url
    embed.set_thumbnail(url=f"{data['profile_pic']}" if data['profile_pic'] else "https://kick.com/img/default-profile-pictures/default1.jpeg") # url, else use default image
    return embed


# helper function
def sort_and_print_names(file_name: str):
    streamers = []
    with open(file_name, 'r') as f:
        streamers = f.read().splitlines()
    streamers.sort()
    with open("sorted_kick.txt", 'w') as file:
        file.writelines('\n'.join(streamers))


def read_streamers(file_name: str):
    streamers = []
    with open(file_name, 'r') as f:
        streamers = f.read().splitlines()

    return streamers


def dt_to_discord_time_stamp(time: datetime) -> str:
    time_float = time.timestamp()
    time_int = int(time_float)
    discord_time_stamp_r = "<t:"+str(time_int)+":R>"
    return discord_time_stamp_r


def format_live_and_not_live_lists(
    live: list[dict],
    not_live: list[dict]
) -> str:
    formatted_string = "🔴 LIVE NOW 🔴 \n"
    formatted_string += "".join([f"- [{data["name"]}]({data["url"]})" +
        (
            f" went live {dt_to_discord_time_stamp(data["start_time"])}\n"
        ) for data in live
    ])

    formatted_string += "\n"

    formatted_string += "⛔ OFFLINE ⛔ \n"

    curr_time = datetime.now(timezone.utc)

    formatted_string += "".join([
        f"{index + 1}. [{data["name"]}]({data["url"]}) " +
        (
            f"(last seen {dt_to_discord_time_stamp(data["start_time"])}\n"
            if curr_time - data["start_time"] < timedelta(days=700)
            else "\n"
        )
        for index, data in enumerate(not_live)
    ])  # timedelta to avoid printing times without valid start_times

    formatted_string += dt_to_discord_time_stamp(datetime.now())

    return formatted_string
