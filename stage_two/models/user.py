from app.db import db
from sqlalchemy import Column, String


class UserModel(db.Model):
    __tablename__ = 'users'

    userId = Column(String, primary_key=True, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String)

    def json(self):
        return {
            'userId': self.userId,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'phone': self.phone
        }

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
