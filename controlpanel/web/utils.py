from zoneinfo import ZoneInfo
from datetime import datetime

from flask import session

from web.config import TZ


def get_main_context():
    return {
        'username': session['user']['username'],
        'user_avatar': session['user']['avatar_url']
    }


def tz_now(tz=TZ):
    tz = ZoneInfo(tz)
    return datetime.now(tz=tz)


def tz_fromiso(iso_date, tz=TZ):
    tz = ZoneInfo(tz)
    return datetime.fromisoformat(iso_date).astimezone(tz)


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix
