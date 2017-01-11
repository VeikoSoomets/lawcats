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
    catlist = memcache.get(str(email) + 'get_categories')
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
          datastore_custom_cats = models.CustomCategory.query(models.CustomCategory.user_id==email).fetch_async()
          if datastore_custom_cats:
            data = [p.to_dict() for p in datastore_custom_cats.get_result()]
            for line in data:
              custom_cats.append({'category_link': line['nice_link'],
                                   'category_name': line['category_name']})
          custom_subcats.append([{'subcategory_name': 'Custom Sources'}, custom_cats])
          custom_maincats.append([{'maincategory_name': 'Custom'}, custom_subcats])
          catlist.extend(custom_maincats)

        memcache.set(str(email) + 'get_categories', catlist, 84400)

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
    limit = self.get_limit(email)
    date_limit = limit[3]
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
      implemented, resolution = self.do_implement(link, email)
    except Exception, e:
      print "Failed to implement source with error message: ", e
      message_type='danger'
      message =_('Could not implement source automatically! Engineers notified!')
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps(data))
      return

    if implemented:
      message_type='success'
      message = _('New source has been implemented! You can test this source in the search page right now!')
      source_request = models.SourceRequest.query(models.SourceRequest.user_id==email, models.SourceRequest.url==url_requested).get()
      source_request.implemented_dtime = datetime.now()
      source_request.put()
      memcache.delete(email + 'get_categories')
    else:
      message_type = 'danger'
      message =_('Could not implement source automatically! Engineers notified!')

    data = {'message': message, 'type': message_type}
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
        return (True, link)
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
        return (True, link)
    except Exception, e:
      print "blogs: ", e
      pass

    return (implemented, resolution)


class StatsHandler(BaseHandler):
  """Handler to create a new requests. """
  @BaseHandler.logged_in2
  def get(self):
    """ Pie & line charts """
    # TODO! Add back!
    """
    conn = base_handler.get_connection()
    cursor = conn.cursor()
    email = self.get_user_email()
    sql = 'SELECT case when queryword="None" then "All updates" else queryword end queryword, SUM(result_cnt) FROM Statistics WHERE user_id="%s" GROUP BY 1' % (email)
    cursor.execute(sql)
    pie_chart = cursor.fetchall()
    # coalesce(result_date,CURRENT_DATE())
    sql2 = 'SELECT date(load_dtime) as result_date, case when queryword="None" then "All updates" else queryword end queryword, SUM(result_cnt) FROM Statistics WHERE user_id="%s" AND date(load_dtime)>=DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY) GROUP BY 1,2 ORDER BY 1 DESC' % (email)
    cursor.execute(sql2)
    line_chart = cursor.fetchall()
    conn.close()
    """
    charts = []
    charts_data = []
    for line in pie_chart:
      charts_data.append({'queryword': (line[0]).encode('utf-8'), 'count': int(line[1])})
    charts.append(charts_data)
    charts_data2=[]
    for line in line_chart:
      charts_data2.append({'result_date': str(line[0]), 'queryword': (line[1]).encode('utf-8'), 'count': int(line[2])})
    numdays = 30
    base = datetime.today()
    date_list = [str((base - timedelta(days=x)).date()) for x in range(0, numdays)]  # create labels for X-axis
    charts.append(charts_data2)

    resultsdict = {'charts': {
      'pie': charts[0],
      'line': {
        'labels': date_list,
        'datasets': charts[1]
      }
    }}
    data = JSONEncoder().encode(resultsdict)
    self.response.out.write(data)


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
    if email not in ['kasparg@gmail.com', 'amltoomas@gmail.com']:
      template_values = {
      'message_type': 'danger',
      'message': 'No admin rights!'
      }
      self.render_template('message.html', template_values)
    else:
      self.get()

  @BaseHandler.logged_in2
  def get(self):
      action = self.request.get('action')
      message=None

      self.buildAdminPage(message=message, message_type='success')

  def buildAdminPage(self, message=None, message_type=None):
    users = models.User.query().order(-models.User.created).fetch()
    faq = models.FAQ.query().fetch()

    new_users = []
    for user in users:
      limit = self.get_limit(user.email_address)
      user.monthly_searches = limit[1]
      dashboard = self.get_dashboard_stats(user.email_address)
      user.new_results = dashboard[0]
      user.old_results = dashboard[1]
      user.qword_count = dashboard[2]
      user.qword_count = dashboard[2]

      if user.usage_expire_date:
        if user.usage_expire_date < datetime.now().date():
          user.usage_expire_date = None

      new_users.append(user)

    template_values = {
      'message_type': message_type,
      'message': message,
      'users': new_users,
      'faq': faq
      }
    self.render_template('sys.html', template_values)


class AdminHandler(BaseHandler): # not really used for now (planned for site admin(
  """Displays the admin page."""

  @BaseHandler.logged_in2
  def post(self):
    self.get()

  @BaseHandler.logged_in2
  def get(self):
      action = self.request.get('action')
      cat_name = str(self.request.get('cat_name'))
      cat_link = self.request.get('cat_link')
      parent_cat = str(self.request.get('parent_cat'))
      message=None
      #print parent_cat

      if action=='create_main':
        cat = models.MainCategories(maincategory_name=cat_name, id=cat_name)
        cat.put()
        message=_('Main category created!')
      elif action=='create_sub':
        cat = models.SubCategories(subcategory_name=cat_name, id=cat_name, parent=ndb.Key('MainCategories', parent_cat))
        cat.put()
        message=_('Sub category created!')
      elif action=='create_cat':
        cat = models.Category(category_name=cat_name, category_link=cat_link, id=cat_name, subcategory_name=parent_cat)
        cat.put()
        message=_('Category created!')

      elif action=='delete_main':
        cat = models.MainCategories.query(models.MainCategories.maincategory_name==cat_name).get(keys_only=True)
        cat.delete()
        message=_('Main category deleted!')
      elif action=='delete_sub':
        cat = models.SubCategories.query(models.SubCategories.subcategory_name==cat_name).get(keys_only=True)
        cat.delete()
        message=_('Sub category deleted!')
      elif action=='delete_cat':
        cat = models.Category.query(models.Category.category_name==cat_name).get(keys_only=True)
        cat.delete()
        message=_('Category deleted!')

      self.buildAdminPage(message=message, message_type='success')

  def buildAdminPage(self, message=None,message_type=None):

    catlist = get_categories()
    faq = models.FAQ.query().fetch()

    template_values = {
      'message_type': message_type,
      'message' : message,
      'catlist' : catlist,
      'faq' : faq
      }
    self.render_template('admin.html', template_values)


PAGE_SIZE = 10
class ResultsHandlerCursor(BaseHandler):

  @classmethod
  @ndb.tasklet
  def callback(self, user_result):
    key = ndb.Key('Results', user_result.result_key.id())
    results = yield key.get_async(use_memcache=True) # seems to be somewhat faster with memcache explicitly set to False, but this does not make sense
    raise ndb.Return(results.to_dict(), {'result_id': user_result.key.id()}, {'tags': user_result.tags}, {'archived': user_result.archived})

  @classmethod
  def merge_dicts(self, x, y, g, h):
    """Given dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    r = z.copy()
    r.update(g)
    z.clear() # test if function consumes less memory then
    u = r.copy()
    u.update(h)
    r.clear()
    return u

  @classmethod
  def get_results(self, cursor, qry):
    """ Get paged results from datastore """
    results, cursor, more = qry.fetch_page(PAGE_SIZE,start_cursor=cursor)#.map(self.callback,options=ndb.QueryOptions(produce_cursors=True))
    results_dicts=[]
    for result in results:
      callback_results = self.callback(result).get_result()
      results_dicts.append(callback_results)

    z2 = [self.merge_dicts(a[0], a[1], a[2], a[3]) for a in results_dicts]

    return z2, cursor, more

  """Displays the results page."""
  @BaseHandler.logged_in2
  def get(self):
    message, message_type= None, None
    template_values = {
      'message': message,
      'message_type': message_type,
      'current_page' : 'results'
    }
    self.render_template('results.html', template_values)


  @BaseHandler.logged_in2
  def post(self):
    email = self.get_user_email()

    """ First try to get variables from json (for some reason needs to be first), then from plain requests. <-- no need for plain request anymore """
    try:
      json_data = json.loads(self.request.body)
      result_id = json_data['result_id']
      action = json_data['action']
    except Exception, e:
      logging.error('did not get all values from json for results handler post request')
      return

    if action == 'get_results':  # TODO! memcache this!
      cursor = None
      bookmark = None
      archived = None
      try:
        json_data = json.loads(self.request.body)
        archived = json_data['archived']
        bookmark = json_data['bookmark']  # with few results there is no bookmark
      except Exception, e:  # seems to be no need for this except
        logging.error(e)

      if bookmark:
        cursor = ndb.Cursor.from_websafe_string(bookmark)

      if not archived:
        archived = None
      qry = models.UserResult.query(models.UserResult.user_id == email, models.UserResult.archived == archived).order(-models.UserResult.load_dtime)
      results, cursor, more = self.get_results(cursor, qry)
      cursor = cursor.urlsafe() if more else None

      resultsdict = {'data': results, 'bookmark': cursor}
      # append to resultsdict list here, and replace memcache with the newly appended results (possibly with cursor)
      data = JSONEncoder().encode(resultsdict)
      self.response.out.write(data)  # give out json

    elif action == 'add_tags':
        if 'json_data' in locals():
          tags = json_data['tags']
        qry5 = models.UserResult.get_by_id(int(result_id))
        for tag in tags:
          if tag not in qry5.tags:
            qry5.tags.append(tag) # add tag
            qry5.put()

        message =_("Tag %s added.") % (str(tags))
        message_type = 'success'
        data = {'message': message, 'type': message_type}
        self.response.out.write(json.dumps((data)))

    elif action == 'remove_tag':
        if 'json_data' in locals():
          tags = json_data['tags']
        qry5 = models.UserResult.get_by_id(int(result_id)) # get datastore object
        qry5.tags.remove(tags) # remove tag
        qry5.put()
        message=_("Tag '%s' removed.") % (tags)
        message_type='success'
        data = {'message': message, 'type': message_type}
        self.response.out.write(json.dumps((data)))

    elif action == 'remove_result':
        id_list = None
        if 'json_data' in locals():
          try:
            id_list = json_data['id_list']
          except Exception:
            pass
        if id_list:
          for result_id in id_list:
            ndb.Key(models.UserResult, int(result_id)).delete()
        else:
          ndb.Key(models.UserResult, int(result_id)).delete()

        message=_("Result removed.")
        message_type='success'
        data = {'message' : message, 'type' : message_type}
        self.response.out.write(json.dumps((data)))
        memcache.delete_multi([email+'_archived_cnt',email+'_new_results',email+'_dashboard',email])

    elif action == 'read_result':
        if 'json_data' in locals():
          read = json_data['read']
          qry5 = models.UserResult.get_by_id(int(result_id))  # get datastore object by key only (save resources)
          qry5.read = read  # True or False
          qry5.put()

    elif action == 'archive_result':
        if 'json_data' in locals():
          archived = json_data['archived']

        qry5 = models.UserResult.get_by_id(int(result_id))  # get datastore object by key only (save resources)
        qry5.archived = archived  # True or False
        qry5.put()

        if archived==True:
          message=_("Result archived.")
          message_type ='success'
        else:
          message = _("Result un-archived.")
          message_type ='success'
        data = {'message' : message, 'type' : message_type}
        self.response.out.write(json.dumps((data)))
        memcache.delete_multi([email + '_archived_cnt', email + '_new_results', email+'_dashboard', email])


class RequestsHandler(BaseHandler):
  """Handler to create a new requests. """

  @BaseHandler.logged_in2
  def get(self):
    email = self.get_user_email()

    if 'application/json' in self.request.headers['Accept']:
      results = memcache.get(email + '_requests')
      catlist = get_categories(email)
      if not results:
        results = models.UserRequest.query(models.UserRequest.user_id == email).fetch()
        memcache.set(email + '_requests', results, 14400)
      resultsdict = {'querywords': results, 'sources': catlist}
      data = JSONEncoder().encode(resultsdict)  # get JSON data... encode, because some fields are of different type.. + just fetch doesn't stringify

      self.response.out.write(data)
    else:
      template_values = {
        'current_page': 'querywords'
      }
      self.render_template('querywords.html', template_values)


  @BaseHandler.logged_in2
  @ndb.toplevel
  def post(self):
    email = self.get_user_email()
    limit = self.get_limit(email)
    monthly_searches_limit_pct = limit[0]
    monthly_searches = limit[1]
    date_limit = limit[3]

    """if not date_limit:
      message = _("Changes will not be applied. If you want to use service without restriction, choose a paid package!")
      #self.render_template('querywords.html', {'message':message, 'message_type':message_type, 'limit_bar' : 0}) # we have to do this to not continue with function
      data = {'message': message, 'type': 'danger'}
      self.response.out.write(json.dumps((data)))
      return"""

    json_data = json.loads(self.request.body)
    queryword = json_data['queryword']

    """ if not queryword:
      message = _('Please enter atleast one queryword!')
      print message
      data = {'message': message, 'type': 'danger'}
      self.response.out.write(json.dumps((data)))
      return """

    action = json_data['action']

    if action == 'create_request':
      request_frequency = json_data['request_frequency']
      categories = json_data['categories']
      splitted_queryword=queryword.split(',')
      # TODO! Search frequency in querywords page to show hours or days

      if monthly_searches_limit_pct>=100:
        message = _('Querywords limit is exceeded. Change search frequencies, remove categories or querywords, or extend limit.')
        data = {'message': message, 'type': 'danger'}
        self.response.out.write(json.dumps((data)))
        return

      if not categories:
        message = _('Please choose atleast one source!')
        data = {'message': message, 'type': 'danger'}
        self.response.out.write(json.dumps((data)))
        return

      qword_limit=1000
      if len(splitted_queryword)>qword_limit:
        message=_("Number of querywords to add in one batch exceeds %s! If you would like to add more than %s querywords in a single operation, please refer to frequently asked questions!") % (qword_limit, qword_limit)
        data = {'message' : message, 'type' : 'danger'}
        self.response.out.write(json.dumps((data)))
        return

      else:
        dbps = []
        for word in splitted_queryword:
          word = word.strip() # remove beginning and leading spaces ()
          if word=='':
            word=None
          qry6 = models.UserRequest.query(ndb.AND(models.UserRequest.user_id == email, models.UserRequest.queryword==word, models.UserRequest.categories.IN(categories))).get(use_memcache=False) # check if we already have such entry by queryword. Implement checking of categories also
          if qry6 is None: # get existing results, check that we don't have same id result already (id is not datastore entity key here, but result_id generated from sql table)
            dbp = models.UserRequest(user_id=email, queryword=word, categories=categories, request_start=datetime.now().date(), request_frequency=int(request_frequency)*60) # , parent=ndb.Key(models.User, 'Items')
            dbps.append(dbp)

        future = ndb.put_multi_async(dbps) # put asyncronously (doesn check if exists)
        ndb.Future.wait_all(future)
        memcache.delete_multi([email+'_requests',email+'_dashboard',email+'_get_limit']) # we now have different requests, remove cache
        AdminSettings.groupmember_monthly_searches(email,monthly_searches) # add monthly search values to usergroup
        message=_('New querywords added!')
        data = {'message' : message, 'type': 'success'}
        self.response.out.write(json.dumps((data)))

    elif action == 'change_frequency': # add limit check (if limit check and frequency is not greater, don't allow)
      request_frequency = json_data['request_frequency']
      request_frequency=int(int(request_frequency)*60) # frequency hours into minutes

      qry6 = models.UserRequest.query(ndb.AND(models.UserRequest.user_id == email, models.UserRequest.queryword==queryword)).get()
      qry6.request_frequency=request_frequency
      qry6.put()
      memcache.delete_multi([email+'_requests',email+'_get_limit']) # we now have different results, so remove from cache
      AdminSettings.groupmember_monthly_searches(email,monthly_searches)  # add monthly search values to usergroup
      
      message=_("Frequency changed for '%s'") % (queryword)
      message_type='success'
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))

    elif action == 'remove_request':
      qry6 = models.UserRequest.query(ndb.AND(models.UserRequest.user_id == email, models.UserRequest.queryword==queryword)).get(keys_only=True)
      qry6.delete()
      memcache.delete_multi([email+'_requests',email+'_dashboard',email+'_get_limit']) # we now have different results, remove cache
      AdminSettings.groupmember_monthly_searches(email,monthly_searches)  # add monthly search values to usergroup
      
      message=_("Request '%s' removed!")  % (queryword)
      message_type='success'
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))

    elif action == 'remove_category':
      single_cat = json_data['single_cat']
      qry6 = models.UserRequest.query(ndb.AND(models.UserRequest.user_id == email, models.UserRequest.queryword==queryword)).get()
      qry6.categories.remove(single_cat) # remove tag
      qry6.put()
      memcache.delete_multi([email+'_requests',email+'_get_limit']) # we now have different results, so remove from cache
      AdminSettings.groupmember_monthly_searches(email,monthly_searches) # add monthly search values to usergroup
      
      message=_("Category '%s' removed!")  % (single_cat)
      message_type='success'
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))

    elif action == 'add_categories': # from plain request
      categories = json_data['categories']
      qry6 = models.UserRequest.query(ndb.AND(models.UserRequest.user_id == email, models.UserRequest.queryword==queryword)).get()
      for cat in categories:
        if cat not in qry6.categories:
          qry6.categories.append(cat)
          qry6.put() # put to datastore object
      memcache.delete(email + '_get_limit')
      AdminSettings.groupmember_monthly_searches(email,monthly_searches) # add monthly search values to usergroup
      
      message=_('Added categories')
      message_type='success'
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps((data)))


class UserDashboard(BaseHandler):
  """Displays the dashboard page."""
  @BaseHandler.logged_in2
  def get(self):
    if self.logged_in:
      self.build_dashboard()

  def days_hours_minutes(self, td):
    if td.days>1:
      date_text=str(td.days) + ' days ago'
    if td.days==1:
      date_text=str(td.days) + ' day ago'
    if td.days<1:
      date_text=str(td.seconds//3600) + ' hours, ' + str((td.seconds//60)%60) + ' minutes ago'
    return date_text

  def build_dashboard(self):
    email = self.get_user_email()
    dashboard = self.get_dashboard_stats(email)

    events = memcache.get(email + '_events')
    if not events:
      # TODO! Add back!
      """
      conn = base_handler.get_connection()
      if isinstance(conn, basestring):
        self.render_template('message.html', {'message-type': 'danger', 'message': conn})
        return
      cursor = conn.cursor()
      sql3 = 'SELECT load_dtime, date(load_dtime) as date, queryword, SUM(result_cnt) FROM Statistics WHERE user_id="%s" group by 2,3 order by load_dtime desc limit 10' % (email)
      cursor.execute(sql3)
      user_events = cursor.fetchall()
      conn.close()

      events = []
      if user_events:
        for event in user_events:
          minutes_ago = self.days_hours_minutes(datetime.now() - event[0])
          event_count = int(event[3])
          event_queryword = event[2]
          if event_queryword == 'None':
            event_queryword = _('All updates')
          event_name = 'new results for "' + event_queryword + '"'
          params={
            'event_name': event_name,
            'minutes_ago': minutes_ago,
            'event_count': event_count
          }
          events.append(params)
        memcache.set(email + '_events', events, 900)  # 15min """

    user_events = []
    # render template
    template_values = {
      'new_results': dashboard[0],
      'old_results': dashboard[1],
      'qword_count': dashboard[2],
      'user_events': events,
      'current_page': 'dashboard'
      }
    self.render_template('dashboard.html', template_values)


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

  @classmethod
  def delete_from_usergroup(self,email,group_name):
    # Remove from Usergroup structured property
    usergroup = models.Usergroup.query(models.Usergroup.group_name == group_name).get()
    if usergroup:
      to_delete = []
      for user in usergroup.users:
        if user.user_email == email:
          to_delete.append(user)  # gather up users, later try "Remove items from a list while iterating in Python" instead
      for a in to_delete:
        usergroup.users.remove(a)
        usergroup.put()

    # also remove from user model
    user = models.User.query(models.User.email_address == email).get()
    user.group_name = None
    user.put()

    memcache.delete_multi([email + '_user_query', email + '_user_group_query'])
    return
    # TODO! add event that user has been removed from group

  @classmethod
  def query_usergroup(self,email):
    usergroup = models.Usergroup.query(models.Usergroup.group_master==email).get() # user email
    #print usergroup
    group_users=[]
    group_name=None
    #for usergroup in usergroups:
    if usergroup:
      group_name=usergroup.group_name
      #if usergroup.users
      for user in usergroup.users:
        user_email=user.user_email
        user_status='pending'
        if user.agreed==False:
            user_status='declined'
        elif user.agreed==True:
            user_status='accepted'
        group_users.append({'user_email':user_email,'user_status':user_status})

    return (group_users,group_name)

  @classmethod
  def groupmember_monthly_searches(self,email,monthly_searches):
    # Add individual monthly searches to usergroup structured property list
    #usergroup = self.get_user_group(email)
    #usergroup = models.Usergroup.query(models.Usergroup.users.user_email==email).get()
    usergroup = self.get_user_group(email)
    #usergroup = models.Usergroup.query(models.Usergroup.users.user_email==email).get() #,agreed=None)])).get()
    if usergroup:
      #print usergroup.users
      for user in list(usergroup.users):  # properties need to be copied to a list, because else you get _basevalues (memcache mutates them)
        if user.user_email==email and user.agreed==True:
          usergroup.users.remove(user)
          new_user=models.Groupmember(user_email=email,agreed=True,monthly_searches=monthly_searches)
          usergroup.users.append(new_user)
          usergroup.put()
          memcache.delete_multi([email+'_user_group_query',email+'_user_query',email+'_get_limit'])
    return

  @classmethod
  def group_to_answer(self,email):
    # Show wheter users has any pending groups
    pending_group = None
    usergroup = self.get_user_group(email)
    #group_date_limit
    if usergroup:
      for user in list(usergroup.users):
        if user.user_email==email and user.agreed==None:
          pending_group = usergroup.group_name

    return pending_group

  @classmethod
  def answer_invitation(self,answer,email,group_name):
    if answer == 'True':
      answer = True
      # put to usermodel
      user = models.User.query(models.User.email_address == email).get() # user email
      user.group_name = group_name
      user.put()

      usergroup = self.get_user_group(email)
      if usergroup:
        for user in list(usergroup.users):
          if email==user.user_email:
            usergroup.users.remove(user)
            new_user=models.Groupmember(user_email=email,agreed=answer)
            usergroup.users.append(new_user)
            usergroup.put()
            memcache.delete(email + '_user_query')

    else:  # if user declines, delete
      self.delete_from_usergroup(email,group_name)
    # put to usergroup
    return
    # add events to both group owner and user (that new user is in a group, or that user has declined)

  def post(self):
    email = self.get_user_email()
    limit = self.get_limit(email)
    date_limit = limit[3]

    action = self.request.get('action')
    if action not in ['answer_usergroup','remove_from_usergroup']:
      json_data = json.loads(self.request.body)
      action = json_data['action']

    if action == 'extend_usage':
      try:
        months = json_data['months']
        packet = json_data['packet']

        if packet == 1:
          search_cnt = 50000
        elif packet == 2:
          search_cnt = 200000  # While saying unlimited, we have this here because we don't believe a user will be using up this much of limits. Else, consider repricing.

        user_query = self.get_user(email)
        old_expire_date = user_query.usage_expire_date
        if not old_expire_date:
          old_expire_date = datetime.now().date()
        expire_date = old_expire_date + timedelta(days=int(months)*30) # for this use from dateutil relativedelta (calculates real months, because length feb != length jan)
        user_query.usage_expire_date = expire_date
        user_query.search_count_limit = int(search_cnt)
        user_query.packet = packet
        user_query.put()

        if user_query.group_name:  # if user belongs to a group (or owns it), permit him to pay for the group
          usergroup = self.get_user_group(email)
          for user in list(usergroup.users):  # properties need to be copied to a list, because else you get _basevalues (memcache mutates them)
            if user.user_email == email and user.agreed == True:
              usergroup.group_date_limit = expire_date
              usergroup.packet = packet
              usergroup.q_word_limit = search_cnt
              usergroup.put()
        memcache.delete_multi([email + '_user_query', email + '_user_group_query', email + '_get_limit'])
        message = _('Payment processed and usage limit extended')
        message_type = 'success'
        data = {'message': message, 'type': message_type}
        self.response.out.write(json.dumps((data)))
        return
      except Exception, e:
        logging.error(e)
        message=str(e)
        message_type = 'danger'
        data = {'message': message, 'type': message_type}
        self.response.out.write(json.dumps((data)))
        return

    elif action == 'change_password':
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

    elif action == "answer_usergroup":
      # group_name = json_data['group_name']
      # answer = json_data['group_answer']
      group_name = self.request.get('group_name')
      answer = self.request.get('group_answer')
      self.answer_invitation(answer,email,group_name)
      memcache.delete_multi([email+'_user_group_query',email+'_user_query',email+'_get_limit'])
      if answer == 'True':
        message = _('Congratulations! You are now member of %s group.') % (group_name)
      else:
        message = _('Declined joining group %s.') % (group_name)
      message_type = 'success'
      data = {'message': message, 'type': message_type}
      #logging.error(message)
      self.buildAdminPage(message=message, message_type=message_type)
      # self.response.out.write(json.dumps((data)))
      return

    elif action == "remove_from_usergroup":
      """ Did not want to duplicate remove_from_usergroup, because leave from usergroup is essentially the same """
      group_name = self.request.get('group_name')
      self_leave = False
      if not group_name:  # if not form action, then angular
        json_data = json.loads(self.request.body)
        group_name = json_data['group_name']
        member_email = json_data['member_email']
      else:  # this is for self-leave
        member_email = email
        self_leave = True
      if not member_email:
        self_leave = True
        member_email = email
      self.delete_from_usergroup(member_email, group_name)
      memcache.delete_multi([email+'_user_group_query',email+'_user_query',member_email+'_get_limit',email+'_get_limit'])
      message = _('User removed from usergroup')
      message_type = 'success'
      data = {'message': message, 'type': message_type}
      if self_leave:
        message = _('You successfully left from usergroup %s') % (group_name)
        self.buildAdminPage(message=message, message_type=message_type)
      else:
        self.response.out.write(json.dumps((data)))
        return

    # Consider checking for date_limit here and warn that this action can't be completed

    elif action == "create_usergroup":
      group_name = json_data['group_name']
      # get limits from user to be cloned to user created group
      limit = self.get_limit(email)
      q_word_limit = limit[2]
      date_limit = limit[3]
      active_packet = limit[4]

      new_group = models.Usergroup(group_name=group_name,group_master=email,group_date_limit=date_limit,q_word_limit=q_word_limit,packet=active_packet)
      new_user = models.Groupmember(user_email=email, agreed=True)  # put creator to same usergroup
      new_group.users.append(new_user)
      new_group.put()
      memcache.delete(email + '_user_query')

      # also change user model entity
      user_model = models.User.query(models.User.email_address == email).get()
      user_model.group_name = group_name
      user_model.put()

      message = _('User group created')
      message_type = 'success'
      data = {'message': message, 'type': message_type}
      #logging.error(message)
      self.response.out.write(json.dumps((data)))
      return

    elif action == "add_to_usergroup":
      group_name = json_data['group_name']
      member_email = json_data['member_email']
      user = models.User.query(models.User.email_address == member_email).get()  # can't get this from cache, because in cache we store session user, not user input
      if user:
        if group_name == user.group_name:
          message = _('User is already in your group!')
          message_type = 'success'
          data = {'message': message, 'type': message_type}
          #logging.error(message)
          self.response.out.write(json.dumps((data)))
          return
        else:
          memcache.delete_multi([email+'_user_group_query',email+'_user_query',member_email+'_user_group_query',member_email+'_user_query'])
          new_user = models.Groupmember(user_email=member_email, agreed=None)
          usergroup = models.Usergroup.query(models.Usergroup.group_name == group_name).get()
          usergroup.users.append(new_user)
          usergroup.put()
          message = _('User invitation sent - user needs to accept invitation.')
          message_type = 'success'
          data = {'message': message, 'type': message_type}
          #logging.error(message)
          self.response.out.write(json.dumps((data)))
          return
      else:
        mailto, name = member_email, member_email
        tyyp = 'invitation'
        verification_url = 'https://www.lawcats.com/signup'
        subject_ = _('lawcats - Invitation by %s!') % (group_name)
        base_handler.sendmail(mailto,subject_,verification_url,name,tyyp)
        message = _('Invitation sent to this e-mail.')
        message_type = 'success'
        data = {'message': message, 'type': message_type}
        #logging.error(message)
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

class RiigiTeatajaDownloadHandler(BaseHandler):

  def get_urls(self):
    src = urllib2.urlopen('https://www.riigiteataja.ee/lyhendid.html', timeout=60)
    urllist = []
    soup = bs4.BeautifulSoup(src)
    soup = soup.find('tbody')
    for result in soup.findAll('tr'):
      law = result.findAll('td')[0]
      linkitem = law.findNext('a', href=True).get('href')
      url = "https://www.riigiteataja.ee/%s?leiaKehtiv" % linkitem
      urllist.append(url)
    return urllist

  @BaseHandler.logged_in2
  def get(self):
      urls = self.get_urls()
      text = urllib2.urlopen(urls[0])
      dbps_main = []
      for url in urls:
        dbp = models.RiigiTeatajaURLs(link=url, text=text.read())
        dbps_main.append(dbp)
      ndb.put_multi(dbps_main)
