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
# Default channel name for ?shift command  # TODO think of a better solution
DEATH_CHANNEL = os.environ.get('DEATH_CHANNEL', 'Víctima del DIABLO STRIKE')
# Commit message on start up config
DEV_CHANNEL_ID = int(os.environ.get('DEV_CHANNEL_ID', 0))
LAST_COMMIT_MSG = os.environ.get('COMMIT_MESSAGE', None)
LAST_COMMIT_BRANCH = os.environ.get('COMMIT_BRANCH', None)

# My Anime List anime info
MAL_MAX_ANIMES = 25959
MAL_ANIMES_PER_PAGE = 50

# Control Panel
CONTROL_PANEL_URL = os.environ.get('CONTROL_PANEL_URL', 'localhost:8000')
CONTROL_PANEL_TOKEN = os.environ.get('CONTROL_PANEL_TOKEN', None)
