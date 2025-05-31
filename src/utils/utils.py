import discord
from dotenv import load_dotenv
import os
import json
from config.logger_config import get_logger
from config.config import DiscordConfig
from datetime import datetime, timedelta, timezone

logger = get_logger(__name__)

discord_config = DiscordConfig(".env")

DISCORD_LIVE_CHANNEL_ID = discord_config.LIVE_CHANNEL_ID


async def send_live_notification(client: discord.Client, notification: discord.Embed):
    id_int = int(DISCORD_LIVE_CHANNEL_ID)
    channel = client.get_channel(id_int)
    logger.info(f"Sending live notification to channel: {channel.name}")
    await channel.send(embed=notification)


def create_embedding(data: json, streaming_platform: str):
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
            color=(5766193 if streaming_platform == "Kick" else 11104511)   # bright green for kick, purple for twitch
        )
    embed.add_field(name=f"{data['title']}", value="")
    embed.set_image(url=f"{data['video_thumbnail']}") # url
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


def read_streamers(file_name : str):
    streamers = []
    with open(file_name, 'r') as f:
        streamers = f.read().splitlines()

    return streamers


def datetime_to_discord_time_stamp(time: datetime) -> str:
    time_float = time.timestamp()
    time_int = int(time_float)
    discord_time_stamp_r ="<t:"+str(time_int)+":R>"  # change last letter to R or F
    return discord_time_stamp_r


def format_streamer_status_list(live: list[dict], not_live: list[dict]) -> str:
    formatted_string = "🔴 LIVE NOW 🔴 \n"
    formatted_string += "".join([f"- [{data["name"]}]({data["url"]})" +
        (
            f" (went live {datetime_to_discord_time_stamp(data["start_time"])})\n"
        ) for data in live
    ])


    formatted_string += "\n"

    formatted_string += "⛔ OFFLINE ⛔ \n"
    formatted_string += "".join([
        f"{index + 1}. [{data["name"]}]({data["url"]})" +
        (
            f" (last seen {datetime_to_discord_time_stamp(data["start_time"])})\n"
            if datetime.now(timezone.utc) - data["start_time"] < timedelta(days=700) else "\n"
        ) for index, data in enumerate(not_live)
    ])  # timedelta to avoid printing times without valid start_times

    formatted_string += datetime_to_discord_time_stamp(datetime.now())

    return formatted_string

def limit_message_length(formatted_string: str) -> str:
    """
    Limit message length to 1899 characters while ensuring it ends with a newline
    
    Why? Discord limits messages to <2000 characters
    """
    if len(formatted_string) > 1900:
        truncated_string = formatted_string[:1900]
    
        # Find the last newline before the 1900th character
        last_newline_index = truncated_string.rfind("\n")

        if last_newline_index != -1:
            truncated_string = truncated_string[:last_newline_index + 1]  # Keep everything up to and including the last newline
        else:
            truncated_string = truncated_string[:1900]  # No newline found, hard limit

        formatted_string = truncated_string  # Update formatted_string
    
    return formatted_string
