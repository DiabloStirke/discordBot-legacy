from flask import render_template, request, redirect, url_for, flash
from app.app import app
from app.models import RoleEnum
from app.utils import ensure_session, ensure_role, get_main_context, tz_now, ordinal


@app.route('/silksong/', methods=['GET'], endpoint='silksong')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def silksong():
    now = tz_now()
    verbose_date = f'{now.strftime("%B")} {ordinal(now.day)} {now.year}'
    context = get_main_context()
    context['date'] = verbose_date
    return render_template('silksong.html', **context), 200
