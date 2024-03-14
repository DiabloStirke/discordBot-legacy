import datetime

from flask import redirect, session, request, render_template, url_for, send_from_directory

from web.auth import AuthBlueprint
from web.models.user import User, RoleEnum
from web.discord_client import DiscordClient, DiscordClientException
from web.utils import get_main_context, tz_now
import web.config as config

dc = DiscordClient(
    client_id=config.DISCORD_CLIENT_ID,
    client_secret=config.DISCORD_CLIENT_SECRET
)

auth = AuthBlueprint('auth', __name__)


def set_session(auth_data):
    session['token'] = auth_data['access_token']
    session['expires'] = tz_now() + datetime.timedelta(seconds=auth_data['expires_in'])
    session['refresh'] = auth_data['refresh_token']

    user_info = dc.me(session['token'])
    user_info['avatar_url'] = dc.get_avatar_url(session['token'])
    session['user'] = user_info


def unset_session():
    session.pop('token', None)
    session.pop('expires', None)
    session.pop('refresh', None)
    session.pop('user', None)


@auth.auth_route('/', required_role=RoleEnum.ADMIN, methods=['GET'])
def index():
    context = get_main_context()
    return render_template('dashboard.html', **context)


@auth.route('/login', methods=['GET'])
def login():
    request_data = request.args.to_dict()
    next_page = request_data.get('next', '/')
    if 'refresh' in request_data:
        refresh = session['refresh']
        try:
            auth_data = dc.refresh_token(refresh)
            set_session(auth_data)
        except DiscordClientException:
            return redirect('/login')

        return redirect(next_page)

    if 'token' in session:
        return redirect(next_page)
    session['next'] = next_page
    return send_from_directory('static', 'login.html')


@auth.route('/logout', methods=['GET'])
def logout():
    if 'token' in session:
        dc.revoke_token(session['token'])
        unset_session()
    return redirect('/login')


@auth.route('/discord-oauth', methods=['GET'])
def discord_oauth2():
    callback = url_for('auth.authorized', _external=True, _scheme=config.PREFERRED_URL_SCHEME)
    authorize_url = dc.get_authorization_url(callback)
    return redirect(authorize_url)


@auth.route('/discord-authorized', methods=['GET'])
def authorized():
    code = request.args.get('code')
    next_page = session.pop('next', '/')
    try:
        callback = url_for('auth.authorized', _external=True, _scheme=config.PREFERRED_URL_SCHEME)
        auth_data = dc.exchange_code(code, callback)
    except DiscordClientException:
        return redirect('/login')
    set_session(auth_data)
    user = User.get_by_id(session['user']['id'])
    if user:
        if user.use_discord_username and (
          user.username != session['user']['username'] or not user.username_matches_discord):
            user.update(username=session['user']['username'], username_matches_discord=True)
        if user.avatar_url != session['user']['avatar_url']:
            user.update(avatar_url=session['user']['avatar_url'])

    return redirect(next_page)
