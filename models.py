# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2015 Kaspar Gering
#

from webapp2_extras import security
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from admin import session

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  email_address = Column(String)
  name = Column(String)
  avatar = Column(String)
  user_id = Column(String)
  #preferred_lang = Column(String)
  last_logout = Column(DateTime)
  usage_expire_date = Column(Date)
  search_count_limit = Column(Integer)
  packet = Column(Integer)
  group_name = Column(String)
  agreed_to_terms = Column(Boolean)

  def set_password(self, raw_password):
    """Sets the password for the current user

    :param raw_password:
        The raw password which will be hashed and stored
    """
    self.password = security.generate_password_hash(raw_password, length=12)

  @classmethod
  def get_by_auth_token(cls, user_id, token, subject='auth'):
    """Returns a user object based on a user ID and token.

    :param user_id:
        The user_id of the requesting user.
    :param token:
        The token string to be verified.
    :returns:
        A tuple ``(User, timestamp)``, with a user object and
        the token timestamp, or ``(None, None)`` if both were not found.
    """
    user = session.query(User).filter(User.id == user_id).first()
    return user, None if user else None, None


class ModelUtils(object):
  def to_dict(self):
    result = super(ModelUtils, self).to_dict()
    result['key'] = self.key.id()  # get the key as a string
    return result


class CustomCategory(Base):
  __tablename__ = 'custom_category'
  id = Column(Integer, primary_key=True)
  user_id = Column(String, ForeignKey('user.id'))
  category_name = Column(String)
  category_link = Column(String)
  nice_link = Column(String)
  category_type = Column(String)


class SourceRequest(Base, ModelUtils):
  __tablename__ = 'source_request'
  id = Column(Integer, primary_key=True)
  user_id = Column(String, ForeignKey('user.id'))
  url = Column(String)
  description = Column(String)
  request_time = Column(DateTime)
  implemented_dtime = Column(DateTime)


class MainCategories(Base):
  __tablename__ = 'main_categories'
  id = Column(Integer, primary_key=True)
  maincategory_name = Column(String)


class SubCategories(Base):
  __tablename__ = 'sub_categories'
  id = Column(Integer, primary_key=True)
  subcategory_name = Column(String)


class Category(Base):
  __tablename__ = 'category'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  link = Column(String)
  lang = Column(String)
  level = Column(Integer)


class UserRequest(Base, ModelUtils):
  __tablename__ = 'user_request'
  id = Column(Integer, primary_key=True)
  user_id = Column(String, ForeignKey('user.id'))
  queryword = Column(String)
  categories = Column(String)
  request_start = Column(Date)
  request_frequency = Column(Integer)  # in minutes
  change_dtime = Column(DateTime)
  last_crawl = Column(DateTime)

  @hybrid_property
  def monthly_searches(self):
    return len(self.categories) * 1440 / float(self.request_frequency) * 30


class Results(Base):
  __tablename__ = 'results'
  id = Column(Integer, primary_key=True)
  queryword = Column(String)
  result_title = Column(String)
  result_link = Column(String)
  result_date = Column(Date)
  categories = Column(String)
  load_dtime = Column(DateTime)


class UserEvents(Base):
  __tablename__ = 'user_events'
  id = Column(Integer, primary_key=True)
  user_id = Column(String, ForeignKey('user.id'))
  event_type = Column(Integer)
  event_count = Column(Integer)
  event_date = Column(Date)
  load_dtime = Column(DateTime)


class UserResult(Base):
  __tablename__ = 'user_result'
  id = Column(Integer, primary_key=True)
  user_id = Column(String, ForeignKey('user.id'))
  results_id = Column(String, ForeignKey('results.id'))
  tags = Column(String)
  load_dtime = Column(DateTime)
  archived = Column(Boolean)
  read = Column(Boolean)


class RiigiTeatajaURLs(Base):
  __tablename__ = 'riigi_teataja_urls'
  id = Column(Integer, primary_key=True)
  title = Column(String)
  link = Column(String)
  text = Column(Text)


class Law(Base):
  __tablename__ = 'law'
  id = Column(Integer, primary_key=True)
  title = Column(String)
  link = Column(String)
  text = Column(Text)


class LawMetaInfo(Base):
  __tablename__ = 'law_meta_info'
  id = Column(Integer, primary_key=True)
  paragraph_number = Column(Integer)
  paragraph_link = Column(String)
  paragraph_title = Column(String)
  paragraph_content = Column(Text)