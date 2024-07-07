from ..db import db
from sqlalchemy import Column, Integer, String, ForeignKey


class UserOrganisation(db.Model):
    __tablename__ = 'user_organisation'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.userId'), nullable=False)
    org_id = Column(String, ForeignKey('organisations.orgId'), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
