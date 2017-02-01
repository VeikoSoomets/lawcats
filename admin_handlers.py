# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 Kaspar Gering

""" Contains the admin request handlers for the app (those that require
user access).
"""

import logging

import json # for ajax requests

#import MySQLdb # not needed if everything is in datastore
#from google.appengine.ext.webapp.util import run_wsgi_app

#import time # needed?
from base_handler import BaseHandler
import base_handler

#import docs
#import errors
#from google.appengine.ext import db
import models
from google.appengine.ext import ndb

#from google.appengine.api import users
#from google.appengine.ext.deferred import defer # use tasklets
#from google.appengine.ext import deferred # use tasklets

from datetime import datetime, date, time, timedelta
import time

#import webapp2

from google.appengine.api import memcache
#from webapp2_extras import i18n

from webapp2_extras.i18n import gettext as _ # i18n

#from collections import Counter # qword frequency, relevancy.. but get this into auto handlers instead

import urllib2

from parsers.custom_source import *

#from auto_handlers import AutoAddSource

#import string, gettext
#_ = gettext.gettext

#_ = i18n.gettext
#message = i18n.gettext('Hello, world!')


def get_categories(email=None):
    cat_mem_name = email.encode('ascii', 'ignore').replace('.','').replace('@','')
    catlist = memcache.get(cat_mem_name + 'get_categories')
    if not catlist:
        main_cats = models.MainCategories.query().fetch_async()
        catlist = []
        for main_cat in main_cats.get_result():
          maincats_list=[]
          maincats_list.append(main_cat)

          sub_cats = models.SubCategories.query(ancestor=ndb.Key(models.MainCategories, main_cat.maincategory_name)).fetch_async()
          sub_cats_list = []
          for sub_cat in sub_cats.get_result():
            cat_list = []
            cats = models.Category.query(models.Category.subcategory_name == sub_cat.key.id()).fetch_async()

            cat_list.append(sub_cat)
            cat_list.append(cats.get_result())

            sub_cats_list.append(cat_list)

          maincats_list.append(sub_cats_list)
          catlist.append(maincats_list)

        if email:
          custom_maincats = []
          custom_subcats = []
          custom_cats = []
          datastore_custom_cats = models.CustomCategory.query(models.CustomCategory.user_id==email).fetch()
          if datastore_custom_cats:
            data = [p.to_dict() for p in datastore_custom_cats]
            for line in data:
              custom_cats.append({'category_link': line['nice_link'],
                                   'category_name': line['category_name']})
            custom_subcats.append([{'subcategory_name': 'Custom Sources'}, custom_cats])
            custom_maincats.append([{'maincategory_name': 'Custom'}, custom_subcats])
            catlist.extend(custom_maincats)

        cat_mem_name = email.encode('ascii', 'ignore').replace('.','').replace('@','')
        memcache.set(cat_mem_name + 'get_categories', catlist)

    return catlist


class RequestSource(BaseHandler):
  """Handler to create a new requests. """

  @BaseHandler.logged_in2
  def post(self):
    json_data = json.loads(self.request.body)
    url_requested = json_data['url']
    description = json_data['description']
    email = self.get_user_email()
    implemented = False
    src = None

    """if not date_limit or date_limit < datetime.now().date():
      message = _('Cannot request sources at this time. Extend your date limit to unlock this feature!')
      message_type = 'danger'
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps(data))
      return"""

    if not description or not url_requested:
      message = _('Please fill both fields!')
      message_type = 'danger'
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps(data))
      return

    link = url_requested
    if not link.startswith('http', 0, 4) or not '.' in link:
      link = 'http://' + link
    try:
      """ We need these headers because sometimes we are forbidden """
      hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}
      req = urllib2.Request(link, headers=hdr)  # , headers=hdr
      urllib2.urlopen(req)

    except Exception, e:
      print e
      message = _('Link %s is not valid! Please make sure it begins with www or http:// and that it can be accessed by yourself.')  % (link)
      message_type = 'danger'
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps((data)))
      return

    existing = models.SourceRequest.query(models.SourceRequest.user_id==email, models.SourceRequest.url==url_requested).get()
    if existing:
      message = _('This link has already been requested by you.')
      message_type = 'danger'
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps((data)))
      return

    # Do datastore entry
    source = models.SourceRequest(user_id=email, url=url_requested, description=description, request_time=datetime.now())
    source.put()

    # Implementing sources live
    try:
      implemented, resolution, impl_title, impl_link = self.do_implement(link, email)
    except Exception, e:
      print "Failed to implement source with error message: ", e
      message_type='danger'
      message =_('Could not implement source automatically! Engineers notified!')
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps(data))
      return

    if implemented:
      message_type='success'
      message = _('New source has been implemented! You can test this source in the search page right now! NB! It may take a few seconds, a refresh might help ;) ')
      source_request = models.SourceRequest.query(models.SourceRequest.user_id==email, models.SourceRequest.url==url_requested).get()
      source_request.implemented_dtime = datetime.now()
      source_request.put()
      cat_mem_name = email.encode('ascii', 'ignore').replace('.','').replace('@','')
      memcache.delete(cat_mem_name + 'get_categories')

    else:
      message_type = 'danger'
      message =_('Could not implement source automatically! Engineers notified!')
    data = {'message': message, 'type': message_type, 'link': impl_link}
    if impl_title != '':
        data['title'] = impl_title
    else:
        data['title'] = description
    self.response.out.write(json.dumps(data))
    return

  def do_implement(self, link, user_id):
    # do implementation
    implemented = False
    resolution = False
    # make sure to add http:// when it is not there
    if not link.startswith( 'http', 0, 4):
        link = 'http://' + link

    """ Try RSS handler """
    try:
      rss_link = find_rss(link)
      if rss_link:
        params = {'user_id': user_id,
                  'category_name': rss_link['title'],
                  'category_link': rss_link['link'],
                  'nice_link': link,
                  'category_type': 'rss_source'}
        models.CustomCategory.create(params)
        return (True, link, rss_link['title'], link)
    except Exception, e:
        print "rss: ", e
        pass

    """ Try blogs handler """
    try:
      blog_result, blog_title = blogs_handler(link)
      if blog_result:
        print "got blogs"
        params = {'user_id': user_id,
                  'category_name': blog_title,
                  'category_link': link,
                  'nice_link': link,
                  'category_type': 'blog_source'}
        models.CustomCategory.create(params)
        return (True, link, blog_title, link)
    except Exception, e:
      print "blogs: ", e
      pass

    return (implemented, resolution, '', link)



class SetLangCookie(BaseHandler):
    """ Set the language cookie (if locale is valid), then redirect back to referrer
    """
    def get(self):
        locale = self.request.get('lang')
        # logging.error('locale from request is: '+locale)
        self.response.set_cookie('locale', locale, max_age = 15724800)  # 26 weeks' worth of seconds

        # redirect to referrer or root
        url = self.request.headers.get('Referer', '/')
        self.redirect(url)


class JSONEncoder(json.JSONEncoder):
    """ For jsonifying results - wouldn't need this if there wasn't any datetime objects in datastore """
    def default(self, o):
        # If this is a key, you might want to grab the actual model.
        if isinstance(o, ndb.Key):
            o = ndb.get(o)
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return str(o)  # Or whatever other date format you're OK with...


class TermsHandler(BaseHandler):
  """Displays front page."""
  @BaseHandler.logged_in2
  def get(self):
    message = None
    template_values = {
        'message': message,
        }
    self.render_template('terms.html', template_values)

  @BaseHandler.logged_in2
  def post(self):
    agreed_to_terms = self.request.get('agreed_to_terms')
    email = self.get_user_email()
    if agreed_to_terms=='True':
      agreed_to_terms=True
      message=_('Agreed to terms!')
    else:
      agreed_to_terms=False
      message=_('Did not agree to terms!')

    sign_terms=models.User.query(models.User.email_address==email).get()
    if sign_terms: # if we get user
      sign_terms.agreed_to_terms=agreed_to_terms
      sign_terms.put()
    else: # else put user to user model
      new_user=models.User(email_address=email,agreed_to_terms=agreed_to_terms)
      new_user.put()

    template_values = {
        'message': message,
        }
    self.render_template('terms.html', template_values)


class SiteAdmin(BaseHandler): # not really used for now (planned for site admin(
  """Displays the admin page."""

  @BaseHandler.logged_in2
  def post(self):
    email = self.get_user_email()
    if email not in ['kasparg@gmail.com', 'veiko.soomets@gmail.com']:
      template_values = {
      'message_type': 'danger',
      'message': 'No admin rights!'
      }
      self.render_template('message.html', template_values)
    else:
      self.get()

  @BaseHandler.logged_in2
  def get(self):
      message=None
      self.buildAdminPage(message=message, message_type='success')

  def buildAdminPage(self, message=None, message_type=None):
    template_values = {
      'message_type': message_type,
      'message': message
      }
    self.render_template('sys.html', template_values)


class CustomCats(BaseHandler):
  """Searches from the web (from implemented sources) """
  def get(self):
    email = self.get_user_email()
    if 'application/json' in self.request.headers['Accept']:
      catlist = models.CustomCategory.query(models.CustomCategory.user_id == email).fetch()
      resultsdict = {'sources': catlist}
      data = JSONEncoder().encode(resultsdict)  # get JSON data... encode, because some fields are of different type.. + just fetch doesn't stringify
      self.response.out.write(data)


class AdminSettings(BaseHandler):
  """Displays the settings page."""
  @BaseHandler.logged_in2
  def get(self):
    email = self.get_user_email()
    if 'application/json' in self.request.headers['Accept']:
      group_members, group_master = self.query_usergroup(email)  # get all members of usergroup
      group_to_answer = self.group_to_answer(email)
      results = {
          'user_email': email,
          'group_members': group_members,
          'group_master': group_master,
          'group_to_answer': group_to_answer,
      }
      resultsdict = {'data': results}
      data = JSONEncoder().encode(resultsdict)  # get JSON data... encode, because some fields are of different type.. + just fetch doesn't stringify
      self.response.out.write(data)
    else:
      self.buildAdminPage()


    if action == 'change_password':
      new_password = json_data['new_password']
      old_password = json_data['old_password']
      if not new_password or not old_password: # we only need this if jquery validation doesn't work (for extra security)
        message = _('Please type both passwords!')
        message_type = 'danger'
        data = {'message' : message, 'type' : message_type}
        #logging.error(message)
        self.response.out.write(json.dumps((data)))
        return
      username = str(''.join(self.user.auth_ids))
      try:
        u = self.auth.get_user_by_password(username, old_password, remember=False, save_session=False)
        user = self.user
        user.set_password(new_password)
        user.put()
        message = _('Password successfully changed!')
        message_type = 'success'
        data = {'message': message, 'type': message_type}
        self.response.out.write(json.dumps((data)))
      except Exception, e:
        message_type = 'danger'
        message = _('Old password is wrong!')
        data = {'message': message, 'type': message_type}
        self.response.out.write(json.dumps((data)))
        return





  def buildAdminPage(self, message=None, message_type=None):
    email = self.get_user_email()
    google_login = email[1]

    # date_limit, monthly_searches, monthly_searches_limit, q_word_limit = None, None, None, None
    group_members, group_master = self.query_usergroup(email)  # get all members of usergroup
    group_to_answer = self.group_to_answer(email)

    # gets a tuple of 4 items from basehandler
    limit = self.get_limit(email)
    monthly_searches_limit_pct = limit[0]
    monthly_searches = limit[1]
    q_word_limit = limit[2]
    date_limit = limit[3]
    active_packet = limit[4]

    catlist = get_categories()

    if date_limit and date_limit < datetime.now().date():
      date_limit = None

    # render template
    template_values = {
      'message_type': message_type,
      'message': message,
      'date_limit': date_limit,  # when will searches expire
      'monthly_searches': monthly_searches, # unique monthly searches
      'q_word_limit': q_word_limit,  # monthly search limit
      'limit_bar': monthly_searches_limit_pct, # for limit bar
      'google_login': google_login,  # check if user has logged in with google
      'active_packet': active_packet,
      'group_members': group_members,
      'group_master': group_master,
      'group_to_answer': group_to_answer,
      'current_page': 'settings',
      'catlist': catlist
      }
    self.render_template('settings.html', template_values)

from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(300)
class RiigiTeatajaDownloadHandler(BaseHandler):
  # TODO! instead of cron jobs running this, switch to task queues instead
  def get_urls(self):

    src = urllib2.urlopen('https://www.riigiteataja.ee/lyhendid.html', timeout=60)
    urllist = []
    soup = bs4.BeautifulSoup(src)
    soup = soup.find('tbody')
    for result in soup.findAll('tr'):
      law = result.findAll('td')[0]
      link = law.findNext('a', href=True).get('href')
      title = law.findNext('a', href=True).get_text()
      url = "https://www.riigiteataja.ee/%s?leiaKehtiv" % link
      urllist.append({'title': title, 'url': url})
    return urllist

  @classmethod
  @ndb.tasklet
  def delete_async_(self, input_object):
      # key = ndb.Key('UserRequest', input_key.id())
      key = input_object.key
      del_future = yield key.delete_async(use_memcache=False)  # faster
      raise ndb.Return(del_future)

  def get(self):
      urls = self.get_urls()
      dbps_meta = []
      dbps_main = []
      models.RiigiTeatajaURLs.query().map(self.delete_async_)
      for url in urls:
        text = urlfetch.fetch(url['url'], method=urlfetch.GET)  # replaced because of timeouts
        dbp = models.RiigiTeatajaURLs(title=url['title'], link=url['url'], text=text.content)
        dbps_main.append(dbp)

      future = ndb.put_multi_async(dbps_main)
      ndb.Future.wait_any(future)

      #message="Operation successful, added %s law files to datastore!" % str(len(dbps_meta))
      #self.render_template('sys.html',{'message_type':'success','message':message})
