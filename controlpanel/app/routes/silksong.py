from flask import render_template, request, redirect, url_for, flash
from app.app import app
from app.models import RoleEnum
from app.utils import ensure_session, ensure_role, get_main_context


@app.route('/silksong/', methods=['GET'], endpoint='silksong')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def silksong():
    context = get_main_context()
    return render_template('silksong.html', **context), 200