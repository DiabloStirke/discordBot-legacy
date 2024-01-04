from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    __abstract__ = True

    ID_FIELD = 'id'

    def update(self, ignore_null=False, **kwargs):
        if ignore_null:
            for key, value in kwargs.items():
                if value is None:
                    continue
                setattr(self, key, value)
        else:
            for key, value in kwargs.items():
                setattr(self, key, value)

        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        return db.session.query(cls).all()

    @classmethod
    def get_by_id(cls, obj_id):
        filter = {cls.ID_FIELD: obj_id}
        return db.session.query(cls).filter_by(**filter).first()

    @classmethod
    def new(cls, **kwargs):
        obj = cls(**kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj


db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()
