from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
from flask import session
from web.utils import ensure_session, ensure_role, get_main_context, tz_now, tz_fromiso, ordinal
from web.models.user import RoleEnum
from web.discord_client import DiscordClient, DiscordClientException
from web.config import DISCORD_BOT_TOKEN

messages = Blueprint('messages', __name__)

@messages.route('/messages', methods=['GET'], endpoint='messages_view')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def messages_view():
    if not str(session['user']['id']) in ['370953016951439361', '369546906449346560']:
        return redirect(url_for('auth.index'))
    return render_template('messages.html', **get_main_context())


@messages.route('/messages', methods=['POST'], endpoint='messages_send')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def messages_send():
    if not str(session['user']['id']) in ['370953016951439361', '369546906449346560']:
        return redirect(url_for('auth.index'))

    message = request.form.get('message')
    if not message:
        flash('No message provided', 'error')
        return render_template('messages.html', **get_main_context())

    try:
        bot_client = DiscordClient(bot_token=DISCORD_BOT_TOKEN)
        bot_client.send_dm('369546906449346560', message)
    except DiscordClientException as e:
        flash('Error sending message', 'error')
        current_app.logger.error(e)
        return render_template('messages.html', **get_main_context())

    flash('Message sent', 'success')
    return render_template('messages.html', **get_main_context())
