import os
from dotenv import load_dotenv


class DiscordConfig:
    """
        Path to .env file
        Example: path=".env"
    """
    def __init__(self, env_file: str = None):
        load_dotenv(env_file)
        self.DISCORD_APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID")
        self.DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
        self.DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
        self.LIVE_CHANNEL_ID = os.environ.get("DISCORD_LIVE_CHANNEL_ID")
        self.STREAMERS_CHANNEL_ID = os.environ.get("STREAMERS_CHANNEL_ID")
        self.STREAMERS_MESSAGE_ID = os.environ.get("STREAMERS_MESSAGE_ID")

        # NEW below --- add to .env file
        self.GAME_CHAT_CHANNEL_ID = os.environ.get("GAME_CHAT_CHANNEL_ID")


class WebhookConfig:
    """
        Path to .env file
        Example: path=".env"
    """
    def __init__(self, env_file: str = None):
        load_dotenv(env_file)
        self.PK_URL = os.environ.get("PK_URL")
        self.DEATH_URL = os.environ.get("DEATH_URL")
        self.DROP_URL = os.environ.get("DROP_URL")
        self.LEVEL_URL = os.environ.get("LEVEL_URL")
        self.QUEST_URL = os.environ.get("QUEST_URL")
        self.DIARY_URL = os.environ.get("DIARY_URL")
        self.COLLECTION_LOG_URL = os.environ.get("COLLECTION_LOG_URL")
        self.CB_ACHIEVEMENT_URL = os.environ.get("CB_ACHIEVEMENT_URL")
        self.CB_TASK_URL = os.environ.get("CB_TASK_URL")
        self.PET_URL = os.environ.get("PET_URL")
        self.PERSONAL_BEST_URL = os.environ.get("PERSONAL_BEST_URL")

        self.PKS_TOTAL_GP_URL = os.environ.get("PKS_TOTAL_GP_URL")
        self.DROPS_TOTAL_GP_URL = os.environ.get("DROPS_TOTAL_GP_URL")
        self.PKS_TOP_URL = os.environ.get("PKS_TOP_URL")
        self.DROPS_TOP_URL = os.environ.get("DROPS_TOP_URL")
        self.INVITED_URL = os.environ.get("INVITED_URL")
        self.LEFT_URL = os.environ.get("LEFT_URL")
        self.BINGO_URL = ""  # FIXME


class TwitchConfig:
    """
        Path to .env file
        Example: path=".env"
    """
    def __init__(self, env_file: str = None):
        load_dotenv(env_file)
        self.TWITCH_REFRESH_TOKEN = os.environ.get("TWITCH_REFRESH_TOKEN")
        self.TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
        self.TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
        self.TWITCH_ACCESS_TOKEN = os.environ.get("TWITCH_ACCESS_TOKEN")
