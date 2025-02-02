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
        return {
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
    # if (messageCategory == "chatjoincount") or (messageCategory == "chatjoinlast"):
    #     #<img=107><col=7f0000>Andytheking has joined.</col>
    #     rsn = ccMessageNoDate.strip()
    #     #loop around , remove <><>rsn:<> but don't remove last <>
    #     while '>' in rsn and rsn.index('>')<(len(rsn)-1):
    #         bracketIndex = rsn.index(">")
    #         #substring eveerything after > and repeat
    #         rsn = rsn[bracketIndex+1:]
    #     #rsn =Andytheking has joined.</col>
    #     #print('rsn is:'+rsn)
    #     endingIndex = rsn.index("has joined")-1
    #     rsn = rsn[0:endingIndex]
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


def extractDrop(ccMessageNoDate: str, messageCategory: MessageCategory) -> str | None:
    # Example of ccMessageNoDate is below:
    #   Dooxsi received special loot from a raid: Masori chaps (210,133,947 coins).   [2022-09-27]

    # Value is within parantheses
    if messageCategory == MessageCategory.DROP and '(' in ccMessageNoDate:
        match = re.search(r':\s*(.*?)\s*\(', ccMessageNoDate)
        if match:
            result = match.group(1)
            return result
    return None


def extractLootValue(ccMessageNoDate: str, messageCategory: MessageCategory) -> str | None:
    """
        Extracts the value from messages that are 
        MessageCategory.PK or MessageCategory.DROP
    """
    # check if character after ( is a digit
    # check if a character before ) is 's' for coin's' in string
    # else remove (unf) or (10) or (full) and then check for coins
    if messageCategory == MessageCategory.PK or MessageCategory.DROP:
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
        return coinsStr.replace(',', '')
    else:
        return None


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
