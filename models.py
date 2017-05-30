# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2015 Kaspar Gering
#

import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb

# webapp2 user auth
import time
import webapp2_extras.appengine.auth.models
from webapp2_extras import security
import datetime


class User(webapp2_extras.appengine.auth.models.User):
  id = ndb.StringProperty()
  email_address = ndb.StringProperty()
  name = ndb.StringProperty()
  avatar = ndb.StringProperty()
  user_id = ndb.StringProperty()
  #preferred_lang = ndb.StringProperty()
  last_logout = ndb.DateTimeProperty()
  usage_expire_date = ndb.DateProperty()
  search_count_limit = ndb.IntegerProperty()
  packet = ndb.IntegerProperty()
  group_name = ndb.StringProperty()
  agreed_to_terms = ndb.BooleanProperty(default=False)

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
    token_key = cls.token_model.get_key(user_id, subject, token)
    user_key = ndb.Key(cls, user_id)
    # Use get_multi() to save a RPC call.
    valid_token, user = ndb.get_multi([token_key, user_key])
    if valid_token and user:
      timestamp = int(time.mktime(valid_token.created.timetuple()))
      return user, timestamp

    return None, None


class ModelUtils(object):
  def to_dict(self):
    result = super(ModelUtils, self).to_dict()
    result['key'] = self.key.id()  # get the key as a string
    return result


class CustomCategory(ndb.Model):
  user_id = ndb.StringProperty()
  category_name = ndb.StringProperty()
  category_link = ndb.StringProperty()
  nice_link = ndb.StringProperty()
  category_type = ndb.StringProperty()

  @classmethod
  def create(cls, params):  # not used
    # Create a new folder.
    prod = cls(
        user_id=params['user_id'],
        category_name=params['category_name'],
        category_link=params['category_link'],
        nice_link=params['nice_link'],
        category_type=params['category_type']
    )
    prod.put()
    return prod


class SourceRequest(ModelUtils, ndb.Model):
  user_id = ndb.StringProperty()
  url = ndb.StringProperty()
  description = ndb.StringProperty()
  request_time = ndb.DateTimeProperty()
  implemented_dtime = ndb.DateTimeProperty()

  @classmethod
  @ndb.tasklet
  def add_implemented_dtime(self, user_request):
    key = ndb.Key('SourceRequest', user_request).get()
    key.implemented_dtime = datetime.datetime.now()
    key.put()
    return


class MainCategories(ndb.Model):
  maincategory_name = ndb.StringProperty()

  @classmethod
  def create(cls, params):
    logging.error(params)
    # Create a new folder.
    prod = cls(
      maincategory_name=params['maincategory_name']
    )
    prod.put()
    return prod

  @classmethod
  def create(cls, params):  # not used
    logging.error(params)
    # Create a new folder.
    prod = cls(
        maincategory_name=params['maincategory_name']
    )
    prod.put()
    return prod


class SubCategories(ndb.Model):
  subcategory_name = ndb.StringProperty()

  @classmethod
  def create(cls, params):  # not used
    logging.error(params)
    # Create a new folder.
    prod = cls(
        subcategory_name=params['subcategory_name'],
        language=params['language']
        # maincategory_key = params['maincategory_key']
    )
    prod.put()
    return prod


class Category(ndb.Model):
  name = ndb.StringProperty()
  link = ndb.StringProperty()
  lang = ndb.StringProperty()
  level = ndb.IntegerProperty()

  @classmethod
  def create(cls, params):  # not used
    # logging.error(params)
    # Create a new folder. 
    prod = cls(
        category_name=params['category_name'],
        category_link=params['category_link'],
        language=params['language']
    )
    prod.put()
    return prod


class UserRequest(ModelUtils, ndb.Model):
  user_id = ndb.StringProperty()
  queryword = ndb.StringProperty()
  categories = ndb.StringProperty(repeated=True)
  request_start = ndb.DateProperty()
  request_frequency = ndb.IntegerProperty()  # in minutes
  change_dtime = ndb.DateTimeProperty(auto_now=True)
  last_crawl = ndb.DateTimeProperty()
  monthly_searches = ndb.ComputedProperty(lambda self: len(self.categories) * 1440 / float(
    self.request_frequency) * 30)  # CAST(1440/r.request_frequency AS DECIMAL(3))*30)

  @classmethod
  @ndb.tasklet
  def add_last_crawl(self, user_request):
    # key = ndb.Key('UserRequest', user_request.key.id())
    key = ndb.Key('UserRequest', user_request).get()
    key.last_crawl = datetime.datetime.now()
    key.put()
    # print key
    return
    """results = yield key.get_async()
    results.last_crawl=datetime.datetime.now()
    results.put_async()
    raise ndb.Return(results) #results.to_dict())"""

  @classmethod
  @ndb.tasklet
  def create_async(cls, params):
    """Create a new entity from a subset of the given params dict values. Do it async in a tasklet. """
    prod = cls(
        user_id=params['user_id'],
        queryword=params['queryword'],
        categories=params['categories'],
        request_start=params['request_start'],
        request_frequency=params['request_frequency'],
        # parent=ndb.Key(User, 'Items')
    )
    yield prod.put_async(use_memcache=False)
    raise ndb.Return(prod)


class Results(ndb.Model):
  queryword = ndb.StringProperty()
  result_title = ndb.StringProperty()
  result_link = ndb.StringProperty()
  result_date = ndb.DateProperty()
  categories = ndb.StringProperty()
  load_dtime = ndb.DateTimeProperty(auto_now_add=True)

  @classmethod
  @ndb.tasklet
  def create_async(cls, params):
    """Create a new entity from a subset of the given params dict values."""
    prod = cls(
        queryword=params['queryword'],
        result_title=params['result_title'],
        result_link=params['result_link'],
        result_date=params['result_date'],
        categories=params['category'],
        id=params['queryword'] + params['category'] + str(params['result_date']) + str(len(params['result_link']))
        # lets create a custom id by combining unique stuff
    )

    key = ndb.Key(cls, params['queryword'] + params['category'] + str(params['result_date']) + str(
      len(params['result_link'])))  # lets see if we have result with same id
    ent = key.get()
    if ent is None:
      yield prod.put_async(use_memcache=False)
      raise ndb.Return(prod)


class UserEvents(ndb.Model):
  user_id = ndb.StringProperty()
  event_type = ndb.IntegerProperty()  # event type 1 = new results found
  event_count = ndb.IntegerProperty()
  event_date = ndb.DateProperty(auto_now_add=True)
  load_dtime = ndb.DateTimeProperty(auto_now_add=True)

  """@classmethod
  @ndb.tasklet
  def get_event_async(user_id):
      user = yield comment.result_key.get_async()
      result['UserEvents'] = { 'event_name' : user.event_name, 'load_dtime' : user.load_dtime }
      raise ndb.Return(result) """

  @classmethod
  @ndb.tasklet
  def create_async(cls, params):
    """Create a new entity from a subset of the given params dict values."""
    prod = cls(
        user_id=params['user_id'],
        event_type=params['event_type'],
        event_count=params['event_count'],
    )
    prod = yield prod.put_async()
    raise ndb.Return(prod)


class UserResult(ndb.Model):
  user_id = ndb.StringProperty()
  result_key = ndb.KeyProperty(kind=Results)
  tags = ndb.StringProperty(repeated=True)
  load_dtime = ndb.DateTimeProperty(auto_now_add=True)
  archived = ndb.BooleanProperty()
  read = ndb.BooleanProperty()  # differentiate read and unread results

  """ Not in use, just for boilerplates """
  @classmethod
  @ndb.tasklet
  def get_result_async(comment):
    result = comment.to_dict()
    user = yield comment.result_key.get_async()
    result['user'] = {'user_id': user.user_id, 'tags': user.tags}
    raise ndb.Return(result)

  @classmethod
  @ndb.tasklet
  def create_async(cls, params):
    """Create a new entity from a subset of the given params dict values."""
    prod = cls(
        user_id=params['user_id'],
        result_key=params['result_key']
    )
    yield prod.put_async(use_memcache=False)
    raise ndb.Return(prod)


class UTF8BlobProperty(ndb.BlobProperty):
    """
    This is a custom blob property for storing unicode text as utf-8.
    Later, we can add storing to GCS if text is too large.
    """
    def __init__(self):
        super(UTF8BlobProperty, self).__init__(default="", compressed=True)

    def _validate(self, text):
        if not isinstance(text, basestring):
            raise TypeError("Expected a basestring, got %s" % text)


# Alternative to saving files to filesystem
class RiigiTeatajaURLs(ndb.Model):
    title = ndb.StringProperty()
    link = ndb.StringProperty()
    text = UTF8BlobProperty()  # http://stackoverflow.com/questions/29148054/the-request-to-api-call-datastore-v3-put-was-too-large-using-objectify-datas


class Law(ndb.Model):
    title = ndb.StringProperty()
    link = ndb.StringProperty()
    text = UTF8BlobProperty()