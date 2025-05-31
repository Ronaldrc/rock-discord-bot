from enum import Enum
import aiohttp
from config.config import WebhookConfig
import re
from config.logger_config import get_logger

logger = get_logger(__name__)

### Get discord webhooks
webhook_config = WebhookConfig(".env")


class MessageCategory(Enum):
    PK = 0
    DEATH = 1
    DROP = 2
    LEVEL = 3
    QUEST = 4
    DIARY = 5
    COLLECTION_LOG = 6
    CB_ACHIEVEMENT = 7
    CB_TASK = 8
    PET = 9
    PERSONAL_BEST = 10
    PKS_TOTAL_GP = 11
    DROPS_TOTAL_GP = 12
    PKS_TOP = 13
    DROPS_TOP = 14
    INVITED = 15
    LEFT = 16
    IDK = 17    # FIXME: if this is assigned, code does not handle all cases


async def sendContentToWebhook(webhook_url: str, message: str) -> None:
    # Format json for POST
    payload = {
        "content": f"{message}"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    # print(f"encoded_message is: {message}")
    # POST to webhook URL
    async with aiohttp.ClientSession() as session:
        async with session.post(url=webhook_url, headers=headers, json=payload) as resp:
            try:
                resp.raise_for_status()
                logger.info(f"Sent content to webhook_url")
            except Exception as e:
                logger.error(f"Failed to send content to webhook_url: {e}")


def getMessageCategory(fullStringNoDate: str) -> dict | None:
    """
        Determine the appropriate webhook url, message, and 
        MessageCategory from an in-game message

        Parameters
        ----------
        fullStringNoDate: str
            Runescape message without the preceding emoji

        Returns
        -------
        dict
            The webhook url, message, and MessageCategory as a dictionary
    """

    #PHRASES
    substringHasDefeated = " has defeated "
    substringDefeatedBy = " defeated by "
    substringHCIMDeath = "has died and lost a life."
    substringHCIMDeath2 = "has died and lost their Hardcore Ironman status."
    substringHCIMDeath3 = "has died and lost their hardcore ironman status."
    substringReceivedADrop = "received a drop:"
    substringReceivedItem = "received an item:"
    substringReceivedARaid = "loot from a raid:"
    substringReceivedAClue= "received a clue item:"
    substringLevel = "has reached"
    substringQuest = "completed a quest:"
    substringPet = "being followed:"
    substringPet2 = "have been followed:"
    substringPet3 = "backpack:"
    substringPet4 = "something special:"
    substringBest = "personal best:"
    substringBest2 = "Size:"
    substringCollection = "collection log item:"
    substringCombatAchievement = "Combat Achievement"
    substringCombatTask = " combat task:"
    substringInviteToClan = "invited into the clan"
    substringLeftClan = "has left the clan"
    
    colonCounter = fullStringNoDate.count(':')

    # If default value is returned, failed to capture all cases!
    messageCategory = MessageCategory.IDK

    content_dict = None

    if colonCounter==0 and substringHasDefeated in fullStringNoDate and "has been defeated by has defeated" not in fullStringNoDate:
        prefix=":skull_crossbones:"
        # pks
        messageCategory = MessageCategory.PK
        url = webhook_config.PK_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==0 and (substringDefeatedBy in fullStringNoDate or substringHCIMDeath in fullStringNoDate or substringHCIMDeath2 in fullStringNoDate or substringHCIMDeath3 in fullStringNoDate):
        prefix=":headstone:"

        # deaths
        messageCategory = MessageCategory.DEATH
        url = webhook_config.DEATH_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif (colonCounter==1 and substringReceivedADrop in fullStringNoDate) or (colonCounter==1 and substringReceivedAClue in fullStringNoDate) or (colonCounter==1 and substringReceivedARaid in fullStringNoDate)or (colonCounter==1 and substringReceivedItem in fullStringNoDate):
        prefix=":moneybag:"

        # drops
        messageCategory = MessageCategory.DROP
        url = webhook_config.DROP_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==0 and substringLevel in fullStringNoDate:
        prefix=":partying_face:"

        # levels
        messageCategory = MessageCategory.LEVEL
        url = webhook_config.LEVEL_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==1 and substringQuest in fullStringNoDate:
        prefix=":tada:"

        # quests
        messageCategory = MessageCategory.QUEST
        url = webhook_config.QUEST_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif (colonCounter==1 and substringPet in fullStringNoDate) or (colonCounter==1 and substringPet2 in fullStringNoDate) or (colonCounter==1 and substringPet3 in fullStringNoDate) or (colonCounter==1 and substringPet4 in fullStringNoDate):
        prefix=":dragon:"

        # pet
        messageCategory = MessageCategory.PET
        url = webhook_config.PET_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }

    elif (substringBest in fullStringNoDate and fullStringNoDate.index(':')>12):
        prefix=":medal:"

        # personal best
        messageCategory = MessageCategory.PERSONAL_BEST
        url = webhook_config.PERSONAL_BEST_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==1 and substringCollection in fullStringNoDate:
        prefix=":closed_book:"

        # collection
        messageCategory = MessageCategory.COLLECTION_LOG
        url = webhook_config.COLLECTION_LOG_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==0 and substringInviteToClan in fullStringNoDate:
        prefix=":slight_smile:"

        # invite to clan
        messageCategory = MessageCategory.INVITED
        url = webhook_config.INVITED_URL

        # removed webhook=line
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==0 and substringLeftClan in fullStringNoDate:
        prefix=":cry:"

        # left clan
        url = webhook_config.LEFT_URL
        messageCategory = MessageCategory.LEFT

        # removed webhook=line
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==0 and "completed" in fullStringNoDate and "diary" in fullStringNoDate:
        prefix=":green_book:"

        # diary
        messageCategory = MessageCategory.DIARY
        url = webhook_config.DIARY_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter==0 and substringCombatAchievement in fullStringNoDate:
        prefix=":blue_book:"

        # combat achievement
        messageCategory = MessageCategory.CB_ACHIEVEMENT
        url = webhook_config.CB_ACHIEVEMENT_URL
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }
    elif colonCounter>=1 and substringCombatTask in fullStringNoDate and "CA_ID" in fullStringNoDate:
        # Example of input string
        #     CA_ID:484|Zhaerdra haw completed a grandmaster task: Phantom Muspah Manipulator

        prefix=":crossed_swords:"

        # combat task
        messageCategory = MessageCategory.CB_TASK
        url = webhook_config.CB_TASK_URL
        fullStringNoDate = fullStringNoDate[fullStringNoDate.index("|") + 1: ]
        content_dict = {
            "url" : url,
            "message" : prefix+" "+fullStringNoDate,
            "category" : messageCategory
        }

    # elif colonCounter==0 and "unlocked" in fullStringNoDate and "League" in fullStringNoDate:
    #     prefix="<:leagues:1165723439596847245>"
    #     url = webhook_config.BINGO_URL
    #     await trySendWebhook(url, prefix+" "+fullStringNoDate)
    # elif colonCounter==0 and "mastery" in fullStringNoDate:
    #     prefix="<:leagues:1165723439596847245>"
    #     url = webhook_config.BINGO_URL
    #     await trySendWebhook(url, prefix+" "+fullStringNoDate)
    # elif colonCounter==0 and ("rank" in fullStringNoDate or "Rank" in fullStringNoDate):
    #     prefix="<:leagues:1165723439596847245>"
    #     url = webhook_config.BINGO_URL
    #     await trySendWebhook(url, prefix+" "+fullStringNoDate)
    # elif colonCounter==0 and ("trophy" in fullStringNoDate or "Trophy" in fullStringNoDate):
    #     prefix="<:leagues:1165723439596847245>"
    #     url = webhook_config.BINGO_URL
    #     await trySendWebhook(url, prefix+" "+fullStringNoDate)
    # elif colonCounter==0 and ("League" in fullStringNoDate or "league" in fullStringNoDate or "Leagues" in fullStringNoDate or "League" in fullStringNoDate):
    #     prefix="<:leagues:1165723439596847245>"
    #     url = webhook_config.BINGO_URL
    #     await trySendWebhook(url, prefix + " " + fullStringNoDate)

    # FIXME: need to handle player-messages? or not?
    # elif (colonCounter==1) and (fullStringNoDate.index(':')<=12):
    # if it made it this far, message is a chatg message sent by a player

    return content_dict if content_dict else None


def extractRSN(ccMessageNoDate: str, messageCategory: MessageCategory) -> str:
    """
        Extract the runescape name (RSN) from an in-game message

        Parameters
        ----------
        ccMessageNoDate: str
            Runescape message without the preceding emoji

        messageCategory: MessageCategory
            Category the message belongs to

        Returns
        -------
        str
            The runescape name the in-game message originated from
    """

    rsn = ""
    if messageCategory == MessageCategory.PK:
        defeatedIndex = ccMessageNoDate.index("defeated")
        rsn = ccMessageNoDate[0:defeatedIndex-5]
    elif messageCategory == MessageCategory.DEATH:
        if "defeated" in ccMessageNoDate:
            defeatedIndex = ccMessageNoDate.index("defeated")
            rsn = ccMessageNoDate[0:defeatedIndex-10]
        elif "has died" in ccMessageNoDate:
            defeatedIndex = ccMessageNoDate.index("has died") #for HC and HGIM deaths
            rsn = ccMessageNoDate[0:defeatedIndex-1]
    elif messageCategory == MessageCategory.DROP:
        receivedIndex = ccMessageNoDate.index("received")
        rsn = ccMessageNoDate[0:receivedIndex-1]
    elif messageCategory == MessageCategory.LEVEL:
        receivedIndex = ccMessageNoDate.index(" has reached ")
        rsn = ccMessageNoDate[0:receivedIndex]
    # elif (messageCategory == "chatcount" or "chatlastmessage") and (ccMessageNoDate.index(':')<=12):
    #     colonIndex = ccMessageNoDate.index(":")
    #     rsn = ccMessageNoDate[0:colonIndex]
    elif (messageCategory == MessageCategory.PERSONAL_BEST):
        end_idx = ccMessageNoDate.index(" has achieved a new")
        rsn = ccMessageNoDate[:end_idx]
    elif messageCategory == MessageCategory.COLLECTION_LOG:
        end_idx = ccMessageNoDate.index(" received")
        rsn = ccMessageNoDate[:end_idx]
    return rsn


def extractBoss(ccMessageNoDate: str, messageCategory: MessageCategory) -> str:
    # Example of ccMessageNoDate is below:
        # steamyplank has achieved a new Zulrah personal best: 1:35
        # Moose World has achieved a new Tombs of Amascut (team size: 5) Expert mode Overall personal best: 29:43
    if messageCategory == MessageCategory.PERSONAL_BEST:
        boss_start_index = ccMessageNoDate.index("has achieved a new ") + 19
        boss_end_index = ccMessageNoDate.index(" personal best:")
        result = ccMessageNoDate[boss_start_index: boss_end_index]
        return result
    else:
        return None


def extractDrop(ccMessageNoDate: str, messageCategory: MessageCategory) -> str | None:
    # Example of ccMessageNoDate is below:
    #   Dooxsi received special loot from a raid: Masori chaps (210,133,947 coins).   [2022-09-27]
    #   BigBossHoss received special loot from a raid: Osmumten's fang.

    # Value is within parantheses
    if messageCategory == MessageCategory.DROP:
        if '(' in ccMessageNoDate:
            match = re.search(r':\s*(.*?)\s*\(', ccMessageNoDate)
            if match:
                result = match.group(1)
                return result
        else:
            # There are no parentheses in the message
            #   Instead, extract from colon+2 to period-1
            result = ccMessageNoDate[ccMessageNoDate.index(':') + 2: -1]
            return result    # exclude last charater
    elif messageCategory == MessageCategory.COLLECTION_LOG:
        start_idx = ccMessageNoDate.index(":") + 2
        end_idx = ccMessageNoDate.index(" (")
        return ccMessageNoDate[start_idx:end_idx]

    return None


async def extractLootValue(ccMessageNoDate: str, messageCategory: MessageCategory) -> str | None:
    """
        Extracts the value from messages that are 
        MessageCategory.PK or MessageCategory.DROP or MessageCategory.DEATH
    """
    # check if character after ( is a digit
    # check if a character before ) is 's' for coin's' in string
    # else remove (unf) or (10) or (full) and then check for coins
    if (messageCategory == MessageCategory.PK) or (messageCategory == MessageCategory.DROP) or (messageCategory == MessageCategory.DEATH):
        try:
            if "(" in ccMessageNoDate:
                # has parentheses
                if(ccMessageNoDate[ccMessageNoDate.index('(')+1].isdigit()) and ccMessageNoDate[ccMessageNoDate.index(')')-1]=='s':
                    coinsBeginIndex = ccMessageNoDate.index('(')+1
                    coinsEndingIndex = ccMessageNoDate.index(')')-6 #subtract "coins" str length
                    coinsStr = ccMessageNoDate[coinsBeginIndex:coinsEndingIndex]
                elif ("(uncharged)" in ccMessageNoDate):
                    # 1 pair of parentheses
                    # Make API call to get real-time price of scythe, shadow, or sanguinesti staff
                    coinsStr = await getRealTimePrice(ccMessageNoDate=ccMessageNoDate)

                    # Add the real time price to the message
                    #   BigBossHoss received special loot from a raid: Tumeken's shadow (uncharged).
                    #   BigBossHoss received special loot from a raid: Tumeken's shadow (uncharged) (1,245,250,000 coins).
                    ccMessageNoDate = ccMessageNoDate[:-1] + f" ({coinsStr} coins)."

                else:
                    #find index of first ')'
                    firstEndParenIndex = ccMessageNoDate.index(')')
                    #substring everything after, to make it a normal string with just one set of (coins) paren
                    ccMessageNoDate = ccMessageNoDate[firstEndParenIndex+1:]
                    #standard parse coins
                    coinsBeginIndex = ccMessageNoDate.index('(')+1
                    coinsEndingIndex = ccMessageNoDate.index(')')-6 #subtract "coins" str length
                    coinsStr = ccMessageNoDate[coinsBeginIndex:coinsEndingIndex]
            else:
                # No parentheses
                # Make API call to get real-time price
                coinsStr = await getRealTimePrice(ccMessageNoDate=ccMessageNoDate)

                # Add the real time price to the message
                #   BigBossHoss received special loot from a raid: Dragon hunter crossbow.
                #   BigBossHoss received special loot from a raid: Dragon hunter crossbow (54,405,000 coins).
                ccMessageNoDate = ccMessageNoDate[:-1] + f" ({coinsStr} coins)."
                
            return ccMessageNoDate, coinsStr.replace(',', '')
        except ValueError as e:
            return ccMessageNoDate, "0"
    else:
        return ccMessageNoDate, "0"


async def getRealTimePrice(ccMessageNoDate: str) -> str:
    """ 
    Price of item is not in the message.

    Make an API request to get real time price of item.
    """

    item_to_id = {
        # Cox items
        "Arcane prayer scroll": "21079",
        "Dexterous prayer scroll": "21034",
        "Twisted buckler": "21000",
        "Dragon hunter crossbow": "21012",
        "Dinh's bulwark": "21015",
        "Ancestral hat": "21018",
        "Ancestral robe top": "21021",
        "Ancestral robe bottom": "21024",
        "Dragon claws": "13652",
        "Elder maul": "21003",
        "Kodai insignia": "21043",
        "Twisted bow": "20997",
        # Toa items
        "Osmumten's fang": "26219",
        "Lightbearer": "25975",
        "Elidinis' ward": "25985",
        "Masori mask": "27226",
        "Masori body": "27229",
        "Masori chaps": "27232",
        "Tumeken's shadow (uncharged)": "27277",    # tumeken shadow (uncharged)
        # Tob items
        "Avernic defender hilt": "22477",
        "Ghrazi rapier": "22324",
        "Sanguinesti staff (uncharged)": "22481",  # Sanguinesti staff (uncharged)
        "Justiciar faceguard": "22326",
        "Justiciar chestguard": "22327",
        "Justiciar legguards": "22328",
        "Scythe of vitur (uncharged)": "22486",  # scythe of vitur (uncharged)
    }
    
    url = "https://prices.runescape.wiki/api/v1/osrs/latest"
    headers = {
        'User-Agent': 'Drops Tracker for discord server',
    }
    params = {
        "id": 1
    }
    # Find substr and store key-value
    item_id = None
    for key, value in item_to_id.items():
        if key in ccMessageNoDate:
            params["id"] = value
            item_id = value
            break
    
    if item_id is not None:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()
                data = data['data'][f"{item_id}"]
                coinsInt = data['low']
            coinsStr = format(coinsInt, ',')
    else:
        coinsStr = "0"

    return coinsStr


def extractTimeInSeconds(ccMessageNoDate: str) -> float:
    pbTimeSeconds=""
    
    startIndex = ccMessageNoDate.index("personal best: ") + 15
    timeStringWithColons = ccMessageNoDate[startIndex:]
    colonCounter = timeStringWithColons.count(':')
    #10:10:10.8-
    if colonCounter == 2:
        pbHoursStr = timeStringWithColons[0:timeStringWithColons.index(":")]
        substringMinutes = timeStringWithColons[timeStringWithColons.index(":")+1:]
        pbMinutesStr = substringMinutes[0:substringMinutes.index(":")]
        substringSeconds = substringMinutes[substringMinutes.index(":")+1:]
        pbTimeSeconds = int(pbHoursStr) * 60 * 60 + int(pbMinutesStr) * 60 + float(substringSeconds)
    elif colonCounter == 1:
        pbMinutesStr = timeStringWithColons[0:timeStringWithColons.index(":")]
        substringSeconds = timeStringWithColons[timeStringWithColons.index(":")+1:]
        pbTimeSeconds = int(pbMinutesStr) * 60 + float(substringSeconds)
    #0:10
    #0:10.8
    return pbTimeSeconds


def checkForBingoDrop(fullStringNoDate: str, content_dict: dict):
    """
        Determine the appropriate webhook url, message, and
        MessageCategory from an in-game message

        Example of an in-game message:
            <:TaskMastericon:1147705076677345322>
            ScytheMane has completed the Hard Kandarin diary\.

        Parameters
        ----------
        fullStringNoDate: str
            Runescape message without the preceding emoji

        Returns
        -------
        dict
            The webhook url, message, and MessageCategory as a dictionary
    """
    if content_dict:
        content_dict["isBingo"] = False  # default value

        bingo_drops = [
            # 3 pairs of Glacial temotli OR pet
            "Glacial temotli",
            "Moxi",
            # Any 2 DT2 uniques OR pet
            "Baron",
            "Butch",
            "Lil'viathan",
            "Wisp",
            "Virtus mask",
            "Virtus robe top",
            "Virtus robe bottom",
            #   duke
            "Magus vestige",
            "Eye of the duke",  # clog
            #   leviathan
            "Venator vestige",
            "Leviathan's lure",     # clog
            #   vardorvis
            "Ultor vestige",
            "Executioner's axe head", # clog
            #   whisperer
            "Bellator vestige",
            "Siren's staff",    # clog
            # 3 colo uniques (excludes quiver) clogs only!! do not show up as drops
            #   OR pet
            "Smol heredit",
            "Sunfire fanatic helm",
            "Sunfire fanatic cuirass",
            "Sunfire fanatic chausses",
            "Tonalztics of ralos",
            "Echo crystal",
            # Zombie axe
            "Broken zombie axe",
            # Zombie helmet
            "Broken zombie helmet",
            # Voidwaker blade
            "Voidwaker blade",
            # Voidwaker hilt
            "Voidwaker hilt",
            # Voidwaker gem
            "Voidwaker gem",
            # Complete chugging barrel (only a collection log)
            "Chugging barrel (disassembled)",
            # 3 ToA uniques
            #   Or Pet
            "Tumeken's guardian",
            "Osmumten's fang",
            "Lightbearer",
            "Elidinis' ward",
            "Masori mask",
            "Masori body",
            "Masori chaps",
            "Tumeken's shadow (uncharged)",
            # 3 ToB uniques
            #  or Pet
            "Lil' zik",
            "Avernic defender hilt",
            "Ghrazi rapier",
            "Sanguinesti staff (uncharged)",  # Sanguinesti staff (uncharged)
            "Justiciar faceguard",
            "Justiciar chestguard",
            "Justiciar legguards",
            "Scythe of vitur (uncharged)",  # scythe of vitur (uncharged)                                         
            # 2 Cox uniques
            #   or pet
            "Olmlet",
            "Twisted buckler",
            "Dragon hunter crossbow",
            "Dinh's bulwark",
            "Ancestral hat",
            "Ancestral robe top",
            "Ancestral robe bottom",
            "Dragon claws",
            "Elder maul",
            "Kodai insignia",
            "Twisted bow",
            # Gauntlet
            "Youngllef",
            "Enhanced crystal weapon seed",
            "Crystal armour seed",
            # All 3 zulrah OR mutagen
            #   or pet
            "Pet snakeling",
            "Magma mutagen", "Tanzanite mutagen",
            "Tanzanite fang", "Magic fang", "Serpentine visage",
            # 5 Fire capes / 1 infernal cape
            #   or pet
            "Tzrek-jad",
            "Jal-nib-rek",
            "Infernal cape",
            "Fire cape",
            # 1 Slayer boss uniques (clan mates will screenshot)
            # Full twinflame staff
            "Fire element staff crown",
            "Ice element staff crown",
            # 2 GOTR uniques
            #   or pet
            "Abyssal protector",
            "Abyssal needle",
            "Abyssal lantern",
            "Abyssal red dye",
            "Abyssal green dye",
            "Abyssal blue dye",
            # Full set OATHPLATE armor
            "Yami",
            "Oathplate helm",
            "Oathplate chest",
            "Oathplate legs",
            # 2 Huey Uniques
            #   or pet
            "Huberte",
            "Hueycoatl hide",
            "Tome of earth (empty)",
            "Dragon hunter wand",
            # 1 sigil drop
            #   or pet
            "Pet dark core",
            "Arcane sigil",
            "Spectral sigil",
            "Elysian sigil",
            # 3 Tomes of water OR pet
            "Tiny tempor",
            "Tome of water (empty)",
            # 2 cudgels
            #   or pet
            "Sraracha",
            "Sarachnis cudgel",
            # 2 Nex drops 
            #   OR pet
            "Zaryte vambraces", "Nihil horn", "Torva full helm (damaged)",
            "Torva platebody (damaged)", "Torva platelegs (damaged)",
            "Ancient hilt",
            "Nexling",
            # 3 Venator shards
            #   or pet
            "Muphin",
            "Venator shard",
            # 1 Crystal tool seed 
            #   OR pet
            "Crystal tool seed",
            "Smolcano",
            # All medium clue boots
            "Ranger boots",
            "Holy sandals",
            "Spiked manacles",
        ]
        
        team_green = [
            "McFrop",
            "SoloDabbd",
            "rambroze",
            "Weave X",
            "Hemlockk",
            "69kaboom420",
            "GART0U",
            "Casey Ellis",
            "Nokowt",
            "davecolis",
            "Farmrr",
            "Baco n",
            "NIEVES STRAP",
            "Yoshi6380",
            "ItsFlowstate",
            "ryanlul",
            "IronBlock460",
            "SogMonkey",
            "drhookahh",
            "CMDRSquiggly",
            "canabisaurus",
            "BaggoWaggo",
            "HC-Chyne",
            "VVaelin",
        ]

        team_blue = [
           "Schm0ke",
           "jibbuh",
           "Slush i",
           "zjoka",
           "Ur left nut",
           "Red EyedXaXa",
           "Hunglllef",
           "OH MY R0D",     # R0D contains a zero
           "ScytheMane",
           "MarlinMerlin",
           "eeguod",
           "OS Rex",
           "War Plane",
           "Saucemanchie",
           "grandsonned",
           "Hara xx",    # xhara?
           "ElectriccK",
           "Rmltorino60",
           "philly788",
           "Bleakpenguin",
           "En pc",
           "BirnDream",
           "RelentlessJr",
           "Pretty Ass",
           "Senpais Cox",
        ]

        team_red = [
            "steamyplank",
            "BigBossHoss",
            "Mike Kent",
            "Waterri",
            "Felix Flail",
            "EternalToad",
            "Endlingg",
            "Maddognathan",
            "z bak",
            "Hotdog Stand",
            "owenowen_IM",
            "Mooselito",
            "Zachs Life",
            "MiniBossHoss",
            "S U S A N O",
            "PSYOPER",
            "R o l i t o",
            "Spahrten",
            "3st3_VATO",
            "SimianMonke",
            "turbo_z31",
            "SirQweaD",
        ]


        # Determine if drop is bingo-related
        for drop in bingo_drops:
            if drop in fullStringNoDate:
                content_dict["isBingo"] = True
                break
        
        # Now determine team - green, blue, red
        if content_dict["isBingo"]:
            for name in team_green:
                if name in fullStringNoDate:
                    # send to green team drop webhook
                    content_dict["teamName"] = "green"
                    return content_dict

            for name in team_blue:
                if name in fullStringNoDate:
                    # send to blue team drop webhook
                    content_dict["teamName"] = "blue"
                    return content_dict

            for name in team_red:
                if name in fullStringNoDate:
                    # send to red team drop webhook
                    content_dict["teamName"] = "red"
                    return content_dict

    return content_dict
