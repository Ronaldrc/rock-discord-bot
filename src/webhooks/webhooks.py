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
    substringJoinClanChat = "has joined."
    substringLeftClanChat = "has left."
    
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
            "category" : messageCategory,
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
    elif colonCounter>=1 and substringCombatTask in fullStringNoDate and (fullStringNoDate.index(':')>12):
        prefix=":crossed_swords:"

        # combat task
        messageCategory = MessageCategory.CB_TASK
        url = webhook_config.CB_TASK_URL
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

    # BINGO
        #   Check for
        #   fang, 2 cox weapons, tome of fire, full moons set
    if content_dict:
        bingo_drops = [
            # 3 fangs
            "Osmumten's fang",
            # 2 Cox weapons
            "Twisted buckler", "Dragon hunter crossbow",
            "Dinh's bulwark", "Dragon claws", "Elder maul", "Kodai insignia",
            "Twisted bow",
            # Tome of fire
            "Tome of fire",
            # A full moons set
            "Eclipse atlatl", "Eclipse moon helm", "Eclipse moon chestplate",
            "Eclipse moon tassets",
            "Dual macuahuitl", "Blood moon helm", "Blood moon chestplate",
            "Blood moon tassets",
            "Blue moon spear", "Blue moon helm", "Blue moon chestplate",
            "Blue moon tassets",
            # Medium clue boots
            "Ranger boots", "Wizard boots", "Holy sandals", "Spiked manacles",
            "Climbing boots (g)"
            # Any full godsword
            "Godsword shard", "Ancient hilt", "Armadyl hilt", "Bandos hilt",
            "Saradomin hilt", "Zamorak hilt"
            # Master clue ornament kit
            "Occult ornament kit", "Torture ornament kit", "Anguish ornament kit",
            "Tormented ornament kit", "Dragon defender ornament kit",
            "Armadyl godsword ornament kit", "Bandos godsword ornament kit",
            "Saradomin godsword ornament kit", "Zamorak godsword ornament kit",
            "Dragon platebody ornament kit", "Dragon kiteshield ornament kit",
            # Any vestige
            "vestige",
            # Any rev weapon
            "Craw's bow", "Thammaron's sceptre", "Viggora's chainmace",
            # Scurrius pet
            "Scurry",
            # 2 Nex drops
            "Zaryte vambraces", "Nihil horn", "Torva full helm (damaged)",
            "Torva platebody (damaged)", "Torva platelegs (damaged)",
            "Ancient hilt",
            # Zolcano item
            "Crystal tool seed", "Zalcano shard", "Smolcano",
            # Master wand
            "Master wand"
            # 2 obby armor pieces
            "Obsidian helmet", "Obsidian platebody", "Obsidian platelegs",
            "Toktz-ket-xil", "Obsidian cape",
            # All 3 zulrah OR mutagen
            "mutagen", "Tanzanite fang", "Magic fang", "Serpentine visage",
            # Corp sigil
            "Arcane sigil", "Elysian sigil", "Spectral sigil",
            # Moxy or Huberte pet
            "Moxi", "Huberte",
            # Mole slippers
            "Mole slippers",
            # Noxious hally - 3 pieces
            "Noxious point", "Noxious blade", "Noxious pommel",
            # Cerb crystal
            "Primordial crystal", "Pegasian crystal", "Eternal crystal",
            "Smouldering stone",
            # 3 aranea boots
            "Aranea boots",
            # Earth warrior champion scroll
            "Earth warrior champion scroll",
            # Teleport anchoring scroll
            "Teleport anchoring scroll",
            # Golden tench
            "Golden tench"
        ]

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
        colonIndex = ccMessageNoDate.index(" has achieved a new")
        rsn = ccMessageNoDate[0:colonIndex]
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
            #   Instead, extract from colon + 2 to . - 1
            result = ccMessageNoDate[ccMessageNoDate.index(':') + 2: -1]
            return result    # exclude last charater
    return None


async def extractLootValue(ccMessageNoDate: str, messageCategory: MessageCategory) -> str | None:
    """
        Extracts the value from messages that are 
        MessageCategory.PK or MessageCategory.DROP
    """
    # check if character after ( is a digit
    # check if a character before ) is 's' for coin's' in string
    # else remove (unf) or (10) or (full) and then check for coins
    if messageCategory == MessageCategory.PK or messageCategory == MessageCategory.DROP:
        try:
            if "(" in ccMessageNoDate:
                # has parentheses
                if(ccMessageNoDate[ccMessageNoDate.index('(')+1].isdigit()) and ccMessageNoDate[ccMessageNoDate.index(')')-1]=='s':
                    coinsBeginIndex = ccMessageNoDate.index('(')+1
                    coinsEndingIndex = ccMessageNoDate.index(')')-6 #subtract "coins" str length
                    coinsStr = ccMessageNoDate[coinsBeginIndex:coinsEndingIndex]
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
                    "Tumeken's shadow (uncharged)": "27277",
                    # Tob items
                    "Avernic defender hilt": "22477",
                    "Ghrazi rapier": "22324",
                    "Sanguinesti staff (uncharged)": "22481",
                    "Justiciar faceguard": "22326",
                    "Justiciar chestguard": "22327",
                    "Justiciar legguards": "22328",
                    "Scythe of vitur (uncharged)": "22486",
                }

                
                url = "https://prices.runescape.wiki/api/v1/osrs/latest"
                headers = {
                    'User-Agent': 'Drops Tracker for discord server',
                }
                params = {
                    "id": 1    # must change
                }
                # Find substr and store key-value
                for key, value in item_to_id.items():
                    if key in ccMessageNoDate:
                        params["id"] = value
                        item_id = value
                        break

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, headers=headers) as resp:
                        data = await resp.json()
                        data = data['data'][f"{item_id}"]
                        coinsInt = data['low']
                    coinsStr = format(coinsInt, ',')
                
            return coinsStr.replace(',', '')
        except ValueError as e:
            return "0"
    else:
        return "0"


def extractTimeInSeconds(ccMessageNoDate: str) -> str:
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
        content_dict["is_bingo"] = False  # default value

        bingo_drops = [
            # 3 fangs
            "Osmumten's fang",
            # 2 Cox weapons
            "Dragon hunter crossbow",
            "Dinh's bulwark", "Dragon claws", "Elder maul", "Kodai insignia",
            "Twisted bow",
            # Tome of fire
            "Tome of fire",
            # A full moons set
            "Eclipse atlatl", "Eclipse moon helm", "Eclipse moon chestplate",
            "Eclipse moon tassets",
            "Dual macuahuitl", "Blood moon helm", "Blood moon chestplate",
            "Blood moon tassets",
            "Blue moon spear", "Blue moon helm", "Blue moon chestplate",
            "Blue moon tassets",
            # Medium clue boots
            "Ranger boots", "Wizard boots", "Holy sandals", "Spiked manacles",
            "Climbing boots (g)",
            # Any full godsword
            "Godsword shard", "Ancient hilt", "Armadyl hilt", "Bandos hilt",
            "Saradomin hilt", "Zamorak hilt",
            # Master clue ornament kit
            "Occult ornament kit", "Torture ornament kit", "Anguish ornament kit",
            "Tormented ornament kit", "Dragon defender ornament kit",
            "Armadyl godsword ornament kit", "Bandos godsword ornament kit",
            "Saradomin godsword ornament kit", "Zamorak godsword ornament kit",
            "Dragon platebody ornament kit", "Dragon kiteshield ornament kit",
            # Any vestige
            "vestige",
            # Any rev weapon
            "Craw's bow", "Thammaron's sceptre", "Viggora's chainmace",
            # Scurrius pet
            "Scurry",
            # 2 Nex drops
            "Zaryte vambraces", "Nihil horn", "Torva full helm (damaged)",
            "Torva platebody (damaged)", "Torva platelegs (damaged)",
            "Ancient hilt",
            # Zolcano item
            "Crystal tool seed", "Zalcano shard", "Smolcano",
            # Master wand
            "Master wand",
            # 2 obby armor pieces
            "Obsidian helmet", "Obsidian platebody", "Obsidian platelegs",
            # All 3 zulrah OR mutagen
            "Magma mutagen", "Tanzanite mutagen",
            "Tanzanite fang", "Magic fang", "Serpentine visage",
            # Corp sigil
            "Arcane sigil", "Elysian sigil", "Spectral sigil",
            # Moxy or Huberte pet
            "Moxi", "Huberte",
            # Mole slippers
            "Mole slippers",
            # Noxious hally - 3 pieces
            "Noxious point", "Noxious blade", "Noxious pommel",
            # Cerb crystal
            "Primordial crystal", "Pegasian crystal", "Eternal crystal",
            "Smouldering stone",
            # 3 aranea boots
            "Aranea boots",
            # Earth warrior champion scroll
            "Earth warrior champion scroll",
            # Teleport anchoring scroll
            "Teleport anchoring scroll",
            # Golden tench
            "Golden tench",
            # Merfolk trident
            "Merfolk trident",
        ]
        # 18 names including dabbd out, which is not explicitly written
        team_j22 = [
            "420Caveman",
            "BigBossHoss",
            "Damonster1",
            "HC-Chyne",
            "Hunglllef",
            "Iron H E R B",
            "J-22",
            "jibbuh",
            "Pl0uneR0yale",
            "ryanlul",
            "Saucemanchie",
            "Spahrten",
            "steamyplank",
            "Ur left nut",
            "yea im jebus",
            "GART0U",
            "m8t",
        ]
        # 18 names with little rat
        team_vendirz = [
            "Cheeky",
            "elf on duty",
            "JacobPiment",
            "K l W l",
            "Little Rat",
            "MarlinMerlin",
            "Mike Kent",
            "Nokowt",
            "Plankforpurp",
            "Schm0ke",
            "ThatGuyHarm",
            "Toxic Suns",
            "turbo_z31",
            "UlfhednarTaz",
            "Vendirzy", # included both vendirz name since not sure which is being used for bingo
            "vendirz",
            "Waterri",
            "X x o xx",
            "Little Rat",
        ]

        # Determine if drop is bingo-related
        for drop in bingo_drops:
            if drop in fullStringNoDate:
                content_dict["is_bingo"] = True
                break

        # Now determine team - j22 or vendirz
        for name in team_j22:
            if name in fullStringNoDate:
                # send to j22 drop webhook
                content_dict["bingo_team"] = "j22"
                return content_dict

        for name in team_vendirz:
            if name in fullStringNoDate:
                # send to vendirz drop webhook
                content_dict["bingo_team"] = "vendirz"
                return content_dict

    return content_dict
