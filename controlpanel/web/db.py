from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from typing import Self, List


class Base(DeclarativeBase):
    ID_FIELD = 'id'

    def update(self, ignore_null=False, **kwargs) -> None:
        if ignore_null:
            for key, value in kwargs.items():
                if value is None:
                    continue
                setattr(self, key, value)
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)
        self.save()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls, *order_by) -> List[Self]:
        if order_by:
            return cls.execute(cls.select.order_by(*order_by))
        return cls.execute(cls.select)

    @classmethod
    def get_by_id(cls, obj_id) -> Self:
        filter = {cls.ID_FIELD: obj_id}
        return db.session.query(cls).filter_by(**filter).first()

    @classmethod
    def new(cls, **kwargs) -> Self:
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def filter_by(cls, expression) -> List[Self]:
        return cls.execute(cls.select.where(expression))

    @classmethod
    @property
    def select(cls):
        return select(cls)

    @staticmethod
    def execute(select_query) -> List[Self]:
        rows = db.session.execute(select_query).all()
        return [row[0] for row in rows]


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
