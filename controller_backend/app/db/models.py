import datetime
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

from .session import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Audit(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    type = Column(String)
    user = Column(String) ## Column(Integer, ForeignKey(User.id))
    name = Column(String)
    action = Column(String)
    description = Column(String)

class Valve(Base):
    __tablename__ = "valve"

    name = Column(String, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    is_up = Column(Boolean, default=False)
    state = Column(String)
    last_changed = Column(String)
