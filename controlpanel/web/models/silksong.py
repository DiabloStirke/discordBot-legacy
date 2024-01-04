from web.db import db
from typing import override

class SilkSongNews(db.Model):
    __tablename__ = 'silksong_news'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    date = db.Column(db.DateTime)
    author_id = db.Column(db.ForeignKey('users.id'))

    author = db.relationship('User', backref='silksong_news')

    def __repr__(self):
        return f'<SilkSongNews(title={self.title}, date={self.date})>'

    @override
    def update(self, title=None, url=None, date=None):
        return super().update(ignore_null=True, title=title, url=url, date=date)

    @override
    @classmethod
    def new(cls, title, url, date):
        return super().new(title=title, url=url, date=date)
