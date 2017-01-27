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
    sql = 'SELECT case when queryword="None" then "All keywords" else queryword end queryword, SUM(result_cnt) FROM Statistics WHERE user_id="%s" GROUP BY 1' % (email)
    cursor.execute(sql)
    pie_chart = cursor.fetchall()
    # coalesce(result_date,CURRENT_DATE())
    sql2 = 'SELECT date(load_dtime) as result_date, case when queryword="None" then "All keywords" else queryword end queryword, SUM(result_cnt) FROM Statistics WHERE user_id="%s" AND date(load_dtime)>=DATE_ADD(CURRENT_DATE(), INTERVAL -30 DAY) GROUP BY 1,2 ORDER BY 1 DESC' % (email)
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
      
      message=_("Frequency changed for '%s'") % (queryword)
      message_type='success'
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))

    elif action == 'remove_request':
      qry6 = models.UserRequest.query(ndb.AND(models.UserRequest.user_id == email, models.UserRequest.queryword==queryword)).get(keys_only=True)
      qry6.delete()
      memcache.delete_multi([email+'_requests',email+'_dashboard',email+'_get_limit']) # we now have different results, remove cache
      
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
      
      message=_('Added categories')
      message_type='success'
      data = {'message': message, 'type': message_type}
      self.response.out.write(json.dumps((data)))


class CustomCats(BaseHandler):
  """Searches from the web (from implemented sources) """
  def get(self):
    email = self.get_user_email()
    if 'application/json' in self.request.headers['Accept']:
      catlist = models.CustomCategory.query(models.CustomCategory.user_id == email).fetch()
      resultsdict = {'sources': catlist}
      data = JSONEncoder().encode(resultsdict)  # get JSON data... encode, because some fields are of different type.. + just fetch doesn't stringify
      self.response.out.write(data)


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

  @BaseHandler.logged_in2
  def get(self):
      urls = self.get_urls()
      dbps_meta = []
      dbps_main = []
      models.RiigiTeatajaURLs.query().map(self.delete_async_)
      models.RiigiTeatajaMetainfo.query().map(self.delete_async_)
      for url in urls:
        text = urllib2.urlopen(url['url'])
        dbp = models.RiigiTeatajaURLs(title=url['title'], link=url['url'], text=text.read())
        dbp_meta = models.RiigiTeatajaMetainfo(title=url['title'])
        dbps_main.append(dbp)
        dbps_meta.append(dbp_meta)

      future = ndb.put_multi_async(dbps_main)
      future_meta = ndb.put_multi_async(dbps_meta)
      ndb.Future.wait_all(future_meta)
      ndb.Future.wait_all(future)

      message="Operation successful, added %s law files to datastore!" % str(len(dbps_meta))
      self.render_template('sys.html',{'message_type':'success','message':message})
