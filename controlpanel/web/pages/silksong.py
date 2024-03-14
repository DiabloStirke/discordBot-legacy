from flask import render_template, request, redirect, url_for, flash, current_app
from flask import session
from web.auth import AuthBlueprint
from web.models.user import RoleEnum
from web.models.silksong import SilksongNews
from web.utils import get_main_context, tz_now, tz_fromiso, ordinal

silksong = AuthBlueprint('silksong', __name__)


@silksong.auth_route('/silksong/', required_role=RoleEnum.ADMIN, methods=['GET'])
def silksong_get():
    now = tz_now()
    verbose_date = f'{now.strftime("%B")} {ordinal(now.day)} {now.year}'
    context = get_main_context()
    context['date'] = verbose_date

    empty_news = {
        'id': 'new',
        'message': None,
        'date': now,
        'created_at': now,
        'verbose_date': verbose_date,
        'author': {
            'avatar_url': session['user']['avatar_url'],
            'username': session['user']['username']
        }
    }

    silksong_news = SilksongNews.get_all(SilksongNews.date.desc(), SilksongNews.created_at.desc())
    silksong_news.insert(0, empty_news)
    context['news_list'] = silksong_news
    return render_template('silksong.html', **context), 200


@silksong.auth_route('/silksong', required_role=RoleEnum.ADMIN, methods=['POST'])
def silksong_post():
    request_data = request.form
    message = request_data.get('message', None)
    date = request_data.get('date', None)
    date = tz_fromiso(date)

    if not message:
        flash('Please, avoid trying to create an empty Silksong News message.', 'error')
        return redirect(url_for('silksong.silksong_get'))
    elif not date:
        flash('Please enter a valid date, we need to know when there were those news.', 'error')
        return redirect(url_for('silksong.silksong_get'))
    elif date.date() > tz_now().date():
        flash('Please enter a date in the past, we cannot know the future.', 'error')
        return redirect(url_for('silksong.silksong_get'))

    silksong_news = SilksongNews.new(message=message, date=date, author_id=session['user']['id'])

    if silksong_news:
        flash('Silksong News message created successfully.', 'success')

    else:
        flash('Something went wrong while creating the Silksong News message.', 'error')

    return redirect(url_for('silksong.silksong_get'))


@silksong.auth_route(
    '/silksong/<int:silksong_news_id>/delete',
    methods=['POST'],
    required_role=RoleEnum.ADMIN
)
def silksong_delete(silksong_news_id):
    silksong_news = SilksongNews.get_by_id(silksong_news_id)
    if silksong_news:
        silksong_news.delete()
        flash('Silksong News message deleted successfully.', 'success')
    else:
        flash('Invalid Silksong News ID', 'error')

    return redirect(url_for('silksong.silksong_get'))


@silksong.auth_route(
    '/silksong/<int:silksong_news_id>/edit',
    methods=['POST'],
    required_role=RoleEnum.ADMIN
)
def silksong_edit(silksong_news_id):
    request_data = request.form
    message = request_data.get('message', None)
    date = request_data.get('date', None)
    date = tz_fromiso(date)
    if not message:
        flash('Please, avoid trying to save an empty Silksong News message.', 'error')
        return redirect(url_for('silksong.silksong_get'))
    elif not date:
        flash('Please enter a valid date, we need to know when there were those news.', 'error')
        return redirect(url_for('silksong.silksong_get'))
    elif date.date() > tz_now().date():
        flash('Please enter a date in the past, we cannot know the future.', 'error')
        return redirect(url_for('silksong.silksong_get'))

    silksong_news = SilksongNews.get_by_id(silksong_news_id)
    current_app.logger.info(message)
    current_app.logger.info(date)
    current_app.logger.info(silksong_news)
    if silksong_news:
        silksong_news.message = message
        silksong_news.date = date
        silksong_news.save()
        flash('Silksong News message edited successfully.', 'success')
    else:
        flash('Invalid Silksong News ID', 'error')

    return redirect(url_for('silksong.silksong_get'))
