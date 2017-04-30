# -*- coding: utf-8 -*-
#!/usr/bin/env python

#
# Copyright 2014 Kaspar Gering
"""Contains the non-admin request handlers for the app."""

from base_handler import BaseHandler
from admin_handlers import get_categories
import json

from parsers.bureau_parse import LawfirmParsers
from parsers import ministry_parse,  eurlex_parse, rss_parse, riigiteataja_parse, custom_source

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import memcache

from datetime import datetime, date, time

from webapp2_extras.i18n import gettext as _

from parsers.custom_source import *
import models
from constants import Abbreviations
from services import CategoryService, SearchService


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



class IndexHandler(BaseHandler):
  """Displays front page."""
  def get(self):
    self.render_template('landing.html',{})


class List_Search(BaseHandler):
  """Searches from EU and USA sanctions list. """  
  def post(self):
    try:
      json_data = json.loads(self.request.body)
      query =  json_data['queryword']
      action = json_data['action']
      category = json_data['categories']
      querywords = set(query.split(','))
    except Exception:
      query=self.request.get('queryword')
      action=self.request.get('action')
      querywords=set(query.split(',')) # add to a set

    search_results=[]
    
    for cat in category:
    
      if cat=='OFAC_search':
        index = search.Index(name="SDN_list")
        for query in querywords:
          query_string = 'sdn_name: ~"%s"' % (query)
          try:
              results = index.search(query_string)
              for result in results:
                params={'programs' : result.field('programs').value,
                  'name' : result.field('sdn_name').value, 
                  #'sdn_type' : result.field('sdn_type').value # normalize with EU sanctions data structure
                  }
                search_results.append(params)
          except search.Error:
            logging.exception('Search failed') 
            pass
      
      if cat=='EU_search':
        index = search.Index(name="EU_list")
        for query in querywords:
          query_string = 'name: ~"%s"' % (query)
          try:
              results = index.search(query_string)
              for result in results:
                params={'programs' : result.field('program').value,
                  'name' : result.field('name').value
                  }
                search_results.append(params)
          except search.Error:
            logging.exception('Search failed') 
            pass
    
    message=_('No search results')
    message_type='danger'
    if search_results: # we don't want to add empty values to our list
      message=_('Search successful')
      message_type='success'
    else:
      logging.error('did not get data from backend')
    
    template_values = {
      'message': message,
      'message_type': message_type,
      'search_results': search_results,
      }
      
    if 'json_data' in locals(): # for testing, provide different responses dependant on request type
      resultsdict = {'search_results' : search_results, 'message' : message, 'message_type' : message_type }
      data = JSONEncoder().encode(resultsdict)
      self.response.out.write(data)
    else:
      self.render_template('search.html', template_values)


class WebSearch(BaseHandler):
  """Searches from the web (from implemented sources) """
  @BaseHandler.logged_in2
  def get(self):
    email = self.get_user_email()
    if 'application/json' in self.request.headers['Accept']:
      catlist = get_categories(email)
      resultsdict = {'sources': catlist}
      data = JSONEncoder().encode(resultsdict)
      self.response.out.write(data)
    else:
      catlist = get_categories(email)
      template_values = {
          'catlist' : catlist,
          'current_page': 'search'
        }
      self.render_template('search.html', template_values)
  
  def post(self):
    email = self.get_user_email()

    json_data = json.loads(self.request.body)
    query = json_data['queryword']
    query_string = query.upper().encode('utf-8')
    querywords = set(query.split(' '))

    # List for shorter law names like 'KarS' etc
    lyhendid_in_query_string = [Abbreviations.get_value_by_name(lyhend).decode('utf-8') for lyhend in
                                Abbreviations.get_constant_names(uppercase=True) if lyhend in query_string.split(' ')]
    # List for longer law names like 'Karistusseadustik' etc
    lyhendid_values_in_query_string = [Abbreviations.get_name_by_value(lyhend).decode('utf-8') for lyhend in
                                       Abbreviations.get_constant_values(uppercase=True) if lyhend in query_string.split(' ')]

    if lyhendid_in_query_string:
      querywords.update(lyhendid_in_query_string)
    if lyhendid_values_in_query_string:
      querywords.update(lyhendid_values_in_query_string)

    category = json_data['categories']
    action = json_data['action']
    
    search_results = []
    search_results1 = []

    if action == 'search':
      date_algus = '2014-01-01'
      search_results1 = do_search(querywords, category, date_algus)

    elif action == 'custom_search':
      date_algus = '2014-01-01'
      logging.error(email)
      search_results1 = custom_search(querywords, category, date_algus,email)

    # There are different result set structures for different search types
    if search_results1:  # we don't want to add empty values to our final search list
      for result in search_results1:
        params = {'result_link': result[0],
                  'result_title': result[1],
                  'result_date': result[2],
                  'queryword': result[3],
                  'categories': result[4]
                  }
        search_results.append(params)
          
    if search_results:
      message=_('Got %s results') % str(len(search_results))
      message_type='success'
    else:
      message=_('Did not find any results - try changing your query or add more sources')
      message_type='danger'

    resultsdict = {'search_results': search_results, 'message': message, 'message_type': message_type}
    data = JSONEncoder().encode(resultsdict)
    
    if not data:
      logging.error('did not get data')
    
    self.response.out.write(data)


class Search(BaseHandler):
  """Searches from the web (from implemented sources) """

  @BaseHandler.logged_in2
  def get(self):
    email = self.get_user_email()
    if 'application/json' in self.request.headers['Accept']:
      categories = CategoryService.get(email)
      data = JSONEncoder().encode({'sources': categories})
      self.response.out.write(data)
    else:
      categories = CategoryService.get(email)
      self.render_template('search.html', {
        'categories': categories,
        'current_page': 'search'
      })

  @BaseHandler.logged_in2
  def post(self):
    email = self.get_user_email()
    json_data = json.loads(self.request.body)
    query = json_data.get('queryword')
    category = json_data.get('category')
    action = json_data['action']

    if not query or len(query) == 0 or not category:
      return
    query_words = SearchService.get_querywords(query)
    if action == 'search':
      search_results = SearchService.search(query_words, category, '2014-01-01')

    if search_results:
      logging.error(search_results)
      message = _('Got %s results') % str(len(search_results))
      message_type = 'success'
      resultsdict = {'search_results': [
                    {'result_link': result[0],
                    'result_title': result[1],
                    'result_date': result[2],
                    'queryword': result[3],
                    'categories': result[4]
                    } for result in search_results], 'message': message, 'message_type': message_type}
      data = JSONEncoder().encode(resultsdict)
      self.response.out.write(data)


def custom_search(querywords, category, date_algus, email=None):
    """ Searches from all custom sources for given user. """
    search_results = []

    # we want to optimize, so when a user searches, fetch only user custom cats, but when engine does, fetch all cats
    if email:
      custom_sources2 = models.CustomCategory.query(models.CustomCategory.user_id == email).fetch_async()
    else:
      custom_sources2 = models.CustomCategory.query().fetch_async()

    if custom_sources2:
      for custom in custom_sources2.get_result():
        # Otsime rss allikatest
        logging.error(1)
        if custom.category_type == 'rss_source' and category == custom.category_name:
          #search_results.extend(rss_parse.parse_feed(querywords, category, date_algus))
          try:
            logging.error(2)
            search_results.extend(rss_parse.parse_feed(querywords, category, date_algus))
          except Exception, e:
            logging.error('failed with custom rss source')
            logging.error(e)
            pass

        # Otsime blogidest
        if custom.category_type == 'blog_source' and category == custom.category_name:
          try:
            datastore_custom_cats = models.CustomCategory.query(models.CustomCategory.user_id == email).fetch_async()
            data = [p.to_dict() for p in datastore_custom_cats.get_result()]
            for line in data:
              if category==line['category_name']:
                # src = urllib2.urlopen(line['nice_link'])
                blog_results, blog_title = custom_source.blogs_handler(line['nice_link'], querywords, category)
                search_results.extend(blog_results)
          except Exception, e:
            logging.error('failed with custom blog search')
            logging.error(e)
            pass

    return search_results  # link, title, date, qword, category


    
from operator import itemgetter
def do_search(querywords, category, date_algus):
  """ Meant to be used for monitoring news and updates. """
  search_results=[]

  search_list = [
    {'category': 'Riigiteataja uudised', 'results': riigiteataja_parse.search_riigiteataja_uudised},
    #{'category': 'oigusaktid', 'results': riigiteataja_parse.search_oigusaktid},
    {'category': 'RSS allikad', 'results': rss_parse.parse_feed},
    {'category': 'ministeeriumid', 'results': ministry_parse.search_ministry},
    {'category': 'Riigiteataja seadused', 'results': riigiteataja_parse.search_seadused},
    {'category': u'Õigusaktide otsing', 'results': riigiteataja_parse.search_oigusaktid},
    {'category': 'Maa- ja ringkonnakohtu lahendid', 'results': riigiteataja_parse.search_kohtu},  # to avoid duplicates, add space to source

    {'category': 'Eur-Lex eestikeelsete dokumentide otsing', 'results': eurlex_parse.search_eurlex},

    # advokaadibürood (need, mida mainitud pole, on RSS allikate all)
    {'category': u'Advokaadi- ja õigusbürood', 'results': LawfirmParsers.search_bureau},  # map async to tasklet

  ]

  for source in search_list:

    # Otsime ministeeriumitest (mis ei ole RSS)
    if source['category'] == 'ministeeriumid':
      if category in [x[0] for x in ministry_parse.categories]:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with ministeeriumid')
          logging.error(e)
          pass

    # Otsime riigi ja/või KOV õigusaktidest
    if source['category'] == 'oigusaktid':
      if category in [u'Kehtivate KOV õigusaktide otsing',u'Õigusaktide otsing']:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with FI oigusaktid')
          logging.error(e)
          pass

    # Otsime riigiteataja uudistest ( seadusuudised; kohtuuudised; õigusuudised )
    if source['category'] == 'Riigiteataja uudised':
      if category in riigiteataja_parse.categories_uudised:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with riigiteataja uudised')
          logging.error(e)
          pass

    # Otsime RSS allikatest
    if source['category'] == 'RSS allikad':
      #catlist = [key for key, value in rss_parse.categories2] rss_parse.categories2
      if category in [x[0] for x in rss_parse.categories]:  # mitu allikat
        search_results.extend(source['results'](querywords, category, date_algus))

    # Everything else
    if category == source['category']:
      search_results.extend(source['results'](querywords, category, date_algus))
      try:
        search_results.extend(source['results'](querywords, category, date_algus))
      except Exception, e:
        logging.error('failed with singular category search')
        logging.error(e)
        pass

  # Make results unique (if there are overlaps from multiple sources, eg. "Õigusaktide otsing" source
  search_results = [list(x) for x in set(tuple(x) for x in search_results)]

  # TODO! Sort results by date
  #search_results = search_results.sort(key=lambda r: r[2])

  # Sort results by rank (if there is rank)
  try:
    search_results = sorted(search_results, key=itemgetter(5), reverse=True) # TODO! fix
  except Exception:
    pass

  return search_results  # link, title, date, qword, category, rank

