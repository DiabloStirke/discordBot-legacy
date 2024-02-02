from sqlalchemy.orm import Mapped, mapped_column
from web.db import Base
import secrets


class AuthToken(Base):
    __tablename__ = 'auth_tokens'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    token: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f'<AuthToken({(self.name or "Unknown") + ": "}{self.token})>'

    def __str__(self):
        return self.token

    @classmethod
    def get_by_token(cls, token):
        return cls.filter_by(cls.token == token)

    @classmethod
    def generate(cls, name=None):
        token = secrets.token_urlsafe(64)
        return cls.new(token=token, name=name)
