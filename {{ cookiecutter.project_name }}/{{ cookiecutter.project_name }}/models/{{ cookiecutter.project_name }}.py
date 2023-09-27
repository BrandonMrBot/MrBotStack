# coding: utf-8
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    text,
    Unicode,
    UnicodeText,
    ForeignKey,
    ForeignKeyConstraint,
)

from {{ cookiecutter.project_name }}.models.meta import Base

metadata = Base.metadata

class Country(Base):
    __tablename__ = "country"

    cnty_cod = Column(Unicode(3), primary_key=True)
    cnty_name = Column(Unicode(120))
    cnty_iso = Column(Unicode(3))
    cnty_extension = Column(Unicode(10))

class User(Base):
    __tablename__ = "user"

    user_id = Column(Unicode(120), primary_key=True)
    user_name = Column(Unicode(120))
    user_email = Column(Unicode(120))
    user_password = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    user_about = Column(UnicodeText)
    user_cdate = Column(DateTime)
    user_llogin = Column(DateTime)
    user_cnty = Column(ForeignKey("country.cnty_cod"), nullable=True, index=True)
    user_organization = Column(Unicode(120))
    user_active = Column(ForeignKey("status.status_id"), nullable=True, index=True)
    user_role = Column(ForeignKey("role.role_id"), nullable=True, index=True)
    user_apikey = Column(Unicode(64))
    user_password_reset_key = Column(Unicode(64))
    user_password_reset_token = Column(Unicode(64))
    user_password_reset_expires_on = Column(DateTime)
    tags = Column(UnicodeText)
    extras = Column(UnicodeText)

class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(Unicode(120))

class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(Unicode(120))