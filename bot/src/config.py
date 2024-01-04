import os
from zoneinfo import ZoneInfo

DATETIME_STR_FORMAT = '%y-%m-%d_%H:%M:%S'
TZ = "Europe/Madrid"

TZINFO = ZoneInfo(TZ)


DISCORD_BOT_TOKEN = os.environ.get(
    'DISCORD_BOT_TOKEN',
    'OTIzNzE4Mjg5NzQ4Nzg3MjEz.YcUFsg.vpdcbzez_hXfycU5QEVy3-WFVkc'
)
BOT_PREFIX = os.environ.get('BOT_PREFIX', '?')
# Default channel name for ?shift command
DEATH_CHANNEL = os.environ.get('DEATH_CHANNEL', 'Víctima del DIABLO STRIKE') # TODO think of a better solution
 
# Commit message on start up config
DEV_CHANNEL_ID = int(os.environ.get('DEV_CHANNEL_ID', None))
LAST_COMMIT_MSG = os.environ.get('COMMIT_MESSAGE', None)
LAST_COMMIT_BRANCH = os.environ.get('COMMIT_BRANCH', None)

# My Anime List anime info
MAL_MAX_ANIMES = 25959
MAL_ANIMES_PER_PAGE = 50
