import datetime

from flask import redirect, session, request, send_from_directory, render_template

from app.app import app
from app.models import User, RoleEnum
from app.discord_client import DiscordClient, DiscordClientException
from app.utils import ensure_session, ensure_role, get_main_context, tz_now

CALLBACK_URL = '{base}discord-authorized'

dc = DiscordClient(
    client_id='923718289748787213',
    client_secret='KAH4Q5Ad4lDSDOV7yBxbsIzWIjcuoIYP'
)


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


@app.route('/', endpoint='index')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def index():
    context = get_main_context()
    return render_template('dashboard.html', **context)


@app.route('/login')
def login():
    request_data = request.args.to_dict()
    if 'refresh' in request_data:
        refresh = session['refresh']
        try:
            auth_data = dc.refresh_token(refresh)
            set_session(auth_data)
        except DiscordClientException:
            return redirect('/login')

        return redirect('/')

    if 'token' in session:
        return redirect('/')
    return send_from_directory('static', 'login.html')


@app.route('/logout')
def logout():
    if 'token' in session:
        dc.revoke_token(session['token'])
        unset_session()
    return redirect('/login')


@app.route('/discord-oauth', methods=['GET'])
def discord_oauth2():
    authorize_url = dc.get_authorization_url(CALLBACK_URL.format(base=request.url_root))
    return redirect(authorize_url)


@app.route('/discord-authorized', methods=['GET'])
def authorized():
    code = request.args.get('code')
    auth_data = dc.exchange_code(code, CALLBACK_URL.format(base=request.url_root))
    set_session(auth_data)
    user = User.get_by_id(session['user']['id'])
    if user and user.use_discord_username and (
            user.username != session['user']['username'] or not user.username_matches_discord):
        user.update(username=session['user']['username'], username_matches_discord=True)
    return redirect('/')
