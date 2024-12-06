import discord
from dotenv import load_dotenv
import os
import json
from logger_config import get_logger
from datetime import datetime

logger = get_logger(__name__)

load_dotenv(".env")

DISCORD_LIVE_CHANNEL_ID = os.environ.get("DISCORD_LIVE_CHANNEL_ID")

async def send_live_notification(client : discord.Client, notification : discord.Embed):
    try:
        id_int = int(DISCORD_LIVE_CHANNEL_ID)
        channel = client.get_channel(id_int)
        logger.info(f"Sending live notification to channel: {channel.name}")
        await channel.send(embed=notification)
    except Exception as e:
        logger.error(f"Failed to send live notification to channel: {channel.name}")

def create_embedding(data : json, streaming_platform : str):
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
    embed.set_image(url=f"{data['video_thumbnail']}") # url
    embed.set_thumbnail(url=f"{data['profile_pic']}") # url
    return embed

# helper function
def sort_and_print_names(file_name : str):
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

def datetime_to_discord_time_stamp(time : datetime) -> str:
    time_float = time.timestamp()
    time_int = int(time_float)
    discord_time_stamp_r ="<t:"+str(time_int)+":R>"  # change last letter to R or F
    return discord_time_stamp_r

def format_live_and_not_live_lists(live : list[tuple], not_live : list[tuple], datetime_now : datetime) -> str:
    formatted_string = "🔴 LIVE NOW 🔴 \n"
    formatted_string += "".join([f"{name}\n{url}\n" for (name, url) in live])

    formatted_string += "\n"    # newline in between

    formatted_string += "⛔ OFFLINE ⛔ \n"
    formatted_string += "".join([f"{name}\n{url}\n" for (name, url) in not_live])

    formatted_string += datetime_to_discord_time_stamp(datetime_now)

    return formatted_string