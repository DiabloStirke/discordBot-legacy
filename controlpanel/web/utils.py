from functools import wraps
from zoneinfo import ZoneInfo
from datetime import datetime

from flask import redirect, session, url_for, render_template
from web.models.user import RoleEnum, User

from web.config import TZ

def ensure_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'token' not in session or 'expires' not in session:
            return redirect(url_for('auth.login'))
        if session['expires'] < tz_now():
            redirect(url_for('auth.login', refresh=True))
        return func(*args, **kwargs)
    return wrapper


def ensure_role(role=RoleEnum.ADMIN):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = User.get_by_id(session['user']['id'])
            if not user or user.role < role:
                return render_template('forbidden.html', **get_main_context()), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


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
