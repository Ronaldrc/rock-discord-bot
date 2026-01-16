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
        self.OWNER_ID = os.environ.get("OWNER_ID")
        self.DISCORD_GUILD_ID_PERSONAL = os.environ.get("DISCORD_GUILD_ID_PERSONAL")
        self.DISCORD_GUILD_ID_ROCK = os.environ.get("DISCORD_GUILD_ID_ROCK")
        self.FARMER_USER_ID = os.environ.get("FARMER_USER_ID")


        # PKs
        self.PK_1_HOUR_CHANNEL_ID = int(os.environ.get("PK_1_HOUR_CHANNEL_ID"))
        self.PK_3_HOUR_CHANNEL_ID = int(os.environ.get("PK_3_HOUR_CHANNEL_ID"))
        self.PK_6_HOUR_CHANNEL_ID = int(os.environ.get("PK_6_HOUR_CHANNEL_ID"))
        self.PK_12_HOUR_CHANNEL_ID = int(os.environ.get("PK_12_HOUR_CHANNEL_ID"))
        self.PK_1_DAY_CHANNEL_ID = int(os.environ.get("PK_1_DAY_CHANNEL_ID"))
        self.PK_7_DAY_CHANNEL_ID = int(os.environ.get("PK_7_DAY_CHANNEL_ID"))
        self.PK_30_DAY_CHANNEL_ID = int(os.environ.get("PK_30_DAY_CHANNEL_ID"))

        self.PK_1_HOUR_MESSAGE_ID = int(os.environ.get("PK_1_HOUR_MESSAGE_ID"))
        self.PK_3_HOUR_MESSAGE_ID = int(os.environ.get("PK_3_HOUR_MESSAGE_ID"))
        self.PK_6_HOUR_MESSAGE_ID = int(os.environ.get("PK_6_HOUR_MESSAGE_ID"))
        self.PK_12_HOUR_MESSAGE_ID = int(os.environ.get("PK_12_HOUR_MESSAGE_ID"))
        self.PK_1_DAY_MESSAGE_ID = int(os.environ.get("PK_1_DAY_MESSAGE_ID"))
        self.PK_7_DAY_MESSAGE_ID = int(os.environ.get("PK_7_DAY_MESSAGE_ID"))
        self.PK_30_DAY_MESSAGE_ID = int(os.environ.get("PK_30_DAY_MESSAGE_ID"))

        # Deaths
        self.DEATH_1_HOUR_CHANNEL_ID = int(os.environ.get("DEATH_1_HOUR_CHANNEL_ID"))
        self.DEATH_3_HOUR_CHANNEL_ID = int(os.environ.get("DEATH_3_HOUR_CHANNEL_ID"))
        self.DEATH_6_HOUR_CHANNEL_ID = int(os.environ.get("DEATH_6_HOUR_CHANNEL_ID"))
        self.DEATH_12_HOUR_CHANNEL_ID = int(os.environ.get("DEATH_12_HOUR_CHANNEL_ID"))
        self.DEATH_1_DAY_CHANNEL_ID = int(os.environ.get("DEATH_1_DAY_CHANNEL_ID"))
        self.DEATH_7_DAY_CHANNEL_ID = int(os.environ.get("DEATH_7_DAY_CHANNEL_ID"))
        self.DEATH_30_DAY_CHANNEL_ID = int(os.environ.get("DEATH_30_DAY_CHANNEL_ID"))

        self.DEATH_1_HOUR_MESSAGE_ID = int(os.environ.get("DEATH_1_HOUR_MESSAGE_ID"))
        self.DEATH_3_HOUR_MESSAGE_ID = int(os.environ.get("DEATH_3_HOUR_MESSAGE_ID"))
        self.DEATH_6_HOUR_MESSAGE_ID = int(os.environ.get("DEATH_6_HOUR_MESSAGE_ID"))
        self.DEATH_12_HOUR_MESSAGE_ID = int(os.environ.get("DEATH_12_HOUR_MESSAGE_ID"))
        self.DEATH_1_DAY_MESSAGE_ID = int(os.environ.get("DEATH_1_DAY_MESSAGE_ID"))
        self.DEATH_7_DAY_MESSAGE_ID = int(os.environ.get("DEATH_7_DAY_MESSAGE_ID"))
        self.DEATH_30_DAY_MESSAGE_ID = int(os.environ.get("DEATH_30_DAY_MESSAGE_ID"))

        # Drops
        self.DROP_1_HOUR_CHANNEL_ID = int(os.environ.get("DROP_1_HOUR_CHANNEL_ID"))
        self.DROP_3_HOUR_CHANNEL_ID = int(os.environ.get("DROP_3_HOUR_CHANNEL_ID"))
        self.DROP_6_HOUR_CHANNEL_ID = int(os.environ.get("DROP_6_HOUR_CHANNEL_ID"))
        self.DROP_12_HOUR_CHANNEL_ID = int(os.environ.get("DROP_12_HOUR_CHANNEL_ID"))
        self.DROP_1_DAY_CHANNEL_ID = int(os.environ.get("DROP_1_DAY_CHANNEL_ID"))
        self.DROP_7_DAY_CHANNEL_ID = int(os.environ.get("DROP_7_DAY_CHANNEL_ID"))
        self.DROP_30_DAY_CHANNEL_ID = int(os.environ.get("DROP_30_DAY_CHANNEL_ID"))

        self.DROP_1_HOUR_MESSAGE_ID = int(os.environ.get("DROP_1_HOUR_MESSAGE_ID"))
        self.DROP_3_HOUR_MESSAGE_ID = int(os.environ.get("DROP_3_HOUR_MESSAGE_ID"))
        self.DROP_6_HOUR_MESSAGE_ID = int(os.environ.get("DROP_6_HOUR_MESSAGE_ID"))
        self.DROP_12_HOUR_MESSAGE_ID = int(os.environ.get("DROP_12_HOUR_MESSAGE_ID"))
        self.DROP_1_DAY_MESSAGE_ID = int(os.environ.get("DROP_1_DAY_MESSAGE_ID"))
        self.DROP_7_DAY_MESSAGE_ID = int(os.environ.get("DROP_7_DAY_MESSAGE_ID"))
        self.DROP_30_DAY_MESSAGE_ID = int(os.environ.get("DROP_30_DAY_MESSAGE_ID"))

        # Profit pks
        self.PROFIT_PK_1_HOUR_CHANNEL_ID = int(os.environ.get("PROFIT_PK_1_HOUR_CHANNEL_ID"))
        self.PROFIT_PK_3_HOUR_CHANNEL_ID = int(os.environ.get("PROFIT_PK_3_HOUR_CHANNEL_ID"))
        self.PROFIT_PK_6_HOUR_CHANNEL_ID = int(os.environ.get("PROFIT_PK_6_HOUR_CHANNEL_ID"))
        self.PROFIT_PK_12_HOUR_CHANNEL_ID = int(os.environ.get("PROFIT_PK_12_HOUR_CHANNEL_ID"))
        self.PROFIT_PK_1_DAY_CHANNEL_ID = int(os.environ.get("PROFIT_PK_1_DAY_CHANNEL_ID"))
        self.PROFIT_PK_7_DAY_CHANNEL_ID = int(os.environ.get("PROFIT_PK_7_DAY_CHANNEL_ID"))
        self.PROFIT_PK_30_DAY_CHANNEL_ID = int(os.environ.get("PROFIT_PK_30_DAY_CHANNEL_ID"))

        self.PROFIT_PK_1_HOUR_MESSAGE_ID = int(os.environ.get("PROFIT_PK_1_HOUR_MESSAGE_ID"))
        self.PROFIT_PK_3_HOUR_MESSAGE_ID = int(os.environ.get("PROFIT_PK_3_HOUR_MESSAGE_ID"))
        self.PROFIT_PK_6_HOUR_MESSAGE_ID = int(os.environ.get("PROFIT_PK_6_HOUR_MESSAGE_ID"))
        self.PROFIT_PK_12_HOUR_MESSAGE_ID = int(os.environ.get("PROFIT_PK_12_HOUR_MESSAGE_ID"))
        self.PROFIT_PK_1_DAY_MESSAGE_ID = int(os.environ.get("PROFIT_PK_1_DAY_MESSAGE_ID"))
        self.PROFIT_PK_7_DAY_MESSAGE_ID = int(os.environ.get("PROFIT_PK_7_DAY_MESSAGE_ID"))
        self.PROFIT_PK_30_DAY_MESSAGE_ID = int(os.environ.get("PROFIT_PK_30_DAY_MESSAGE_ID"))

        # Game chat
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
        self.BINGO_DROPS_URL = os.environ.get("BINGO_DROPS_URL")


class KickConfig:
    """
        Path to .env file
        Example: path=".env"
    """
    def __init__(self, env_file: str = None):
        load_dotenv(env_file)
        self.KICK_REFRESH_TOKEN = os.environ.get("KICK_REFRESH_TOKEN")
        self.KICK_CLIENT_ID = os.environ.get("KICK_CLIENT_ID")
        self.KICK_CLIENT_SECRET = os.environ.get("KICK_CLIENT_SECRET")
        self.KICK_ACCESS_TOKEN = os.environ.get("KICK_ACCESS_TOKEN")


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
