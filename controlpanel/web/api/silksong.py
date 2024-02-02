from flask import Blueprint, jsonify
from web.api.utils import token_auth
from web.models.silksong import SilksongNews

silksong_api = Blueprint('silksong_api', __name__, url_prefix='/api/silksong')


@silksong_api.route('news', methods=['GET'], endpoint='news_get')
@token_auth
def news_get():
    """Get all Silksong News messages."""
    silksong_news = SilksongNews.get_all(SilksongNews.date.desc(), SilksongNews.created_at.desc())
    return jsonify([news.toJSON() for news in silksong_news]), 200
