from enum import Enum
from typing import override, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger
from web.db import db, Base

class RoleEnum(Enum):
    ADMIN = 'Admin'
    STAFF = 'Staff'
    USER = 'User'

    def __lt__(self, other):
        if not isinstance(other, RoleEnum):
            return super().__lt__(other)
        if self.value == other.value:
            return False
        if self.value == 'Admin':
            return False
        if self.value == 'Staff' and other.value == 'User':
            return False
        return True

    def __gt__(self, other):
        if not isinstance(other, RoleEnum):
            return super().__gt__(other)
        if self.value == other.value:
            return False
        if self.value == 'User':
            return False
        if self.value == 'Staff' and other.value == 'Admin':
            return False
        return True

    def __eq__(self, other):
        if not isinstance(other, RoleEnum):
            return super().__eq__(other)
        return self.value == other.value

    def __le__(self, other):
        if not isinstance(other, RoleEnum):
            return super().__le__(other)
        return self < other or self == other

    def __ge__(self, other):
        if not isinstance(other, RoleEnum):
            return super().__ge__(other)
        return self > other or self == other

    def __hash__(self):
        return super().__hash__()


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[RoleEnum]
    use_discord_username: Mapped[bool] = mapped_column(default=True)
    username_matches_discord: Mapped[bool] = mapped_column(default=False)
    avatar_url: Mapped[str] = mapped_column(nullable=True)

    silksong_news: Mapped[List['SilksongNews']] = relationship(
        back_populates='author',
        cascade='all, delete-orphan',
        passive_deletes=True
    )


    def __repr__(self):
        return f'<User(name={self.username}, role={self.role.value})>'

    def is_staff(self):
        return self.role in [RoleEnum.ADMIN, RoleEnum.STAFF]

    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    @override
    def update(
            self,
            username=None,
            role=None,
            use_discord_username=None,
            username_matches_discord=None,
            **kwargs
    ):
        if username is not None:
            if self.username != username and self.username_matches_discord:
                self.username_matches_discord = False
            self.username = username
        if role is not None:
            self.role = role
        if use_discord_username is not None:
            if (not self.use_discord_username or not use_discord_username) \
              and self.username_matches_discord:
                self.username_matches_discord = False
            self.use_discord_username = use_discord_username
        if username_matches_discord is not None:
            self.username_matches_discord = username_matches_discord

        return super().update(ignore_null=True, **kwargs)

    @override
    @classmethod
    def new(cls, disc_id, username=None, role=RoleEnum.USER, use_discord_username=True):
        return super().new(
           id=disc_id, username=username, role=role, use_discord_username=use_discord_username
        )

    @staticmethod
    def validate_role(role):
        if not role.upper() in [r.name for r in RoleEnum]:
            return None
        return RoleEnum[role.upper()]
