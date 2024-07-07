from ..db import db
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class OrganisationModel(db.Model):
    __tablename__ = 'organisations'

    orgId = Column(String, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String)

    users = relationship('UserOrganisation', backref='organisation', lazy=True)

    def json(self):
        return {
            'orgId': self.orgId,
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
