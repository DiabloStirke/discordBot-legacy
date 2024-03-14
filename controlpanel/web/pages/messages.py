from flask import render_template, request, redirect, url_for, flash, current_app
from flask import session
from web.auth import AuthBlueprint
from web.utils import get_main_context
from web.models.user import RoleEnum
from web.discord_client import DiscordClient, DiscordClientException
from web.config import DISCORD_BOT_TOKEN

messages = AuthBlueprint('messages', __name__)


@messages.auth_route('/messages', required_role=RoleEnum.ADMIN, methods=['GET'])
def messages_view():
    if not str(session['user']['id']) in ['370953016951439361', '369546906449346560']:
        return redirect(url_for('auth.index'))
    return render_template('messages.html', **get_main_context())


@messages.auth_route('/messages', required_role=RoleEnum.ADMIN, methods=['POST'])
def messages_send():
    if not str(session['user']['id']) in ['370953016951439361', '369546906449346560']:
        return redirect(url_for('auth.index'))

    message = request.form.get('message')
    if not message:
        flash('No message provided', 'error')
        return render_template('messages.html', **get_main_context())

    try:
        bot_client = DiscordClient(bot_token=DISCORD_BOT_TOKEN)
        bot_client.send_dm('334626027961712642', message)
    except DiscordClientException as e:
        flash('Error sending message', 'error')
        current_app.logger.error(e)
        return render_template('messages.html', **get_main_context())

    flash('Message sent', 'success')
    return render_template('messages.html', **get_main_context())
