import click
from flask import Blueprint
from flask.cli import with_appcontext
from web.models.user import User, RoleEnum
from web.models.authtoken import AuthToken

import web.config as config

user_commands = Blueprint('user_commands', __name__, cli_group='users')


@user_commands.cli.command('create-admin')
@click.argument('discord_id', type=int, required=False)
@with_appcontext
def create_admin(discord_id):
    """Create a new admin user.

    DISCORD_ID: The discord ID of the user to create.
    Optional if environment variable CONTROL_PANEL_ADMIN_ID is set.
    """
    if not discord_id:
        discord_id = int(config.CONTROL_PANEL_ADMIN_ID)

    user: User = User.get_by_id(discord_id)
    if user:
        user.update(role=RoleEnum.ADMIN)
        return

    user = User.new(discord_id, None, RoleEnum.ADMIN, True)

    click.echo(f'User {discord_id} created successfully')


@user_commands.cli.command('create-token')
@click.argument('name', type=str, required=False)
@with_appcontext
def create_token(name):
    """Create a new auth token.

    NAME: The name of the token (for easier identification). Optional.
    """
    token = AuthToken.generate(name)
    click.echo(token)
