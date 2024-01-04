from flask import render_template, request, redirect, url_for, flash, Blueprint
from web.models.user import RoleEnum
from web.utils import ensure_session, ensure_role, get_main_context, tz_now, tz_fromiso, ordinal

silksong = Blueprint('silksong', __name__)

@silksong.route('/silksong/', methods=['GET'], endpoint='silksong_get')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def silksong_get():
    now = tz_now()
    verbose_date = f'{now.strftime("%B")} {ordinal(now.day)} {now.year}'
    context = get_main_context()
    context['date'] = verbose_date

    return render_template('silksong.html', **context), 200


@silksong.route('/silksong', methods=['POST'], endpoint='silksong_post')
@ensure_session
@ensure_role(RoleEnum.ADMIN)
def silksong_post():
    request_data = request.form
    message = request_data.get('message', None)
    date = request_data.get('date', None)
    date = tz_fromiso(date)
    print(message, date)

    return redirect(url_for('silksong.silksong_get'))
