from flask import render_template, request, redirect, url_for, flash
from web.auth import AuthBlueprint
from web.models.user import User, RoleEnum
from web.utils import get_main_context


users = AuthBlueprint('users', __name__)


@users.auth_route('/users/', required_role=RoleEnum.ADMIN, methods=['GET'])
def get_users():
    context = get_main_context()
    context['users'] = User.get_all()
    print(context['users'])
    return render_template('users.html', **context), 200


@users.auth_route('/users/new/', required_role=RoleEnum.ADMIN, methods=['POST'])
def new_user():
    request_data = request.form.to_dict()
    disc_id = request_data.get('discord_id', None)
    role = User.validate_role(request_data.get('role', ''))
    username = request_data.get('username', None)
    use_discord_username = bool(request_data.get('from_discord', False))

    if not disc_id:
        flash('Discord-ID is required', 'error')
        return redirect(url_for('users.get_users'))
    user = User.get_by_id(disc_id)

    try:
        disc_id = int(disc_id)
    except ValueError:
        flash('Discord-ID must be a number', 'error')
        return redirect(url_for('users.get_users'))

    if user:
        flash(f'User with id {disc_id} already exists', 'error')
        return redirect(url_for('users.get_users'))

    if not role:
        flash('Invalid role', 'error')
        return redirect(url_for('users.get_users'))

    user = User.new(disc_id, username, role, use_discord_username)

    flash(f'User {disc_id}'
          + f'{" (" + user.username + ")" if user.username else ""} created successfully')
    return redirect(url_for('users.get_users'))


@users.auth_route('/users/<string:disc_id>/delete/', required_role=RoleEnum.ADMIN, methods=['POST'])
def delete_user(disc_id):
    user = User.get_by_id(disc_id)
    if not user:
        flash(f'User with id {disc_id} does not exist', 'error')
        return redirect(url_for('users.get_users'))

    user.delete()

    flash(f'User {disc_id}'
          + f'{" (" + user.username + ")" if user.username else ""} deleted successfully')
    return redirect(url_for('users.get_users'))


@users.auth_route('/users/<string:disc_id>/edit', required_role=RoleEnum.ADMIN, methods=['POST'])
def edit_user(disc_id):
    request_data = request.form.to_dict()
    role = User.validate_role(request_data.get('role', ''))
    user = User.get_by_id(disc_id)
    username = request_data.get('username', None)
    use_discord_username = bool(request_data.get('from_discord', False))

    if not user:
        flash(f'User with id {disc_id} does not exist', 'error')
        return redirect(url_for('users.get_users'))

    if not role:
        flash('Invalid role', 'error')
        return redirect(url_for('users.get_users'))

    user.update(username, role, use_discord_username)

    flash(f'User {disc_id}'
          + f'{" (" + user.username + ")" if user.username else ""} edited successfully')
    return redirect(url_for('users.get_users'))
