__package__ = 'User'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DefaultClause

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(32))
    username = Column(String(10))
    email = Column(String(10))
    password = Column(String(50))
    createtime = Column(String(20))
    lastlogintime = Column(String(20))
    active = Column(Integer, DefaultClause('1')) # 1 : active ; 0 disable
    pubkey = Column(Text(), DefaultClause('None'))

    @property
    def is_active(self):
        if self.active == 1:
            return True
        else:
            return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.uuid
