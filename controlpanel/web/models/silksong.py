import datetime
from typing import Any

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, func
from web.db import Base
from web.utils import ordinal
# from typing import override


class SilksongNews(Base):
    __tablename__ = 'silksong_news'

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(String(1800), nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    author: Mapped['User'] = relationship(back_populates='silksong_news')  # noqa F821 # type: ignore

    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    def __repr__(self):
        return f'<SilkSongNews(By {self.author.username} on {self.date})>'

    def toJSON(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'message': self.message,
            'date': self.date.isoformat(),
        }

    @property
    def verbose_date(self):
        return f'{self.date.strftime("%B")} {ordinal(self.date.day)} {self.date.year}'
