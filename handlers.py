# -*- coding: utf-8 -*-
#!/usr/bin/env python

#
# Copyright 2014 Kaspar Gering
"""Contains the non-admin request handlers for the app."""

from base_handler import BaseHandler
from admin_handlers import get_categories
import json

import archive_search
from parsers.bureau_parse import LawfirmParsers
from parsers import ministry_parse, politsei_parse, fi_parse, eurlex_parse, rss_parse, riigiteataja_parse, riigikohtu_parse, custom_source

from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import memcache

from datetime import datetime, date, time

from webapp2_extras.i18n import gettext as _

from parsers.custom_source import *
import models
import constants


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


class LandingCats(BaseHandler):
  """Searches from the web (from implemented sources) """  
  def get(self):
    if 'application/json' in self.request.headers['Accept']:

      data = memcache.get('landing_cats')
      if not data:
        catlist = models.Category.query(models.Category.category_name.IN(['Business Insider','Postimees',u'Äripäev','EU Sanctions','OFAC Sanctions','Maa- ja ringkonnakohtu lahendid',u'Eelnõude otsing'])).fetch()
        resultsdict = {'sources': catlist}
        data = JSONEncoder().encode(resultsdict)
        memcache.set('landing_cats', data, 84400)

      self.response.out.write(data)


class IndexHandler(BaseHandler):
  """Displays front page."""
  def get(self):
    self.render_template('landing.html',{})


class TermsOfUse(BaseHandler):
  """Displays terms of use page."""
  def get(self):
    self.render_template('terms.html',{})
    
    
class Admin_FAQ(BaseHandler):
  """Displays frequently asked questions page."""
  def get(self):
    faq = memcache.get('faq')
    if faq is None:
      faq = models.FAQ.query(models.FAQ.answered==True).fetch()
      if faq:
        memcache.set('faq',faq)

    template_values = {
        'faq': faq
        }
    self.render_template('faq.html',template_values)
    
  def post(self):
    question = self.request.get('question')
    question_id = self.request.get('question_id')
    answer = self.request.get('answer')
    action = self.request.get('action')
    
    if action=='answer_question':
      qry = models.FAQ.get_by_id(int(question_id))
      qry.answer = answer
      qry.answered = True
      qry.put()
      memcache.delete('faq')
      
      message=_('Answered to question!')
      message_type="success"
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))
      params = {
      'message': message,
      'message_type': 'success'
      }
      #self.render_template('message2.html', params)
      
    elif action=='ask_question':
      qry = models.FAQ(question=question,answered=False)
      qry.put()
      memcache.delete('faq')
      
      message=_('New question posted! We will try to answer that ASAP!')
      message_type="success"
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))
      params = {
      'message': message,
      'message_type': 'success'
      }
      #self.render_template('message2.html', params)
      
    elif action == 'remove_question':
      ndb.Key(models.FAQ, int(question_id)).delete()
      memcache.delete('faq')
      
      message=_("Question removed!")
      message_type='success'
      
      data = {'message' : message, 'type' : message_type}
      self.response.out.write(json.dumps((data)))
      params = {
      'message': message,
      'message_type': 'success'
      }
      #self.render_template('message2.html', params)


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
    try:
      json_data = json.loads(self.request.body)
      query = json_data['queryword']
      query_string = query.upper().encode('utf-8')
      querywords = set(query.split(','))
      if query_string in constants.Lyhendid.get_constant_names(uppercase=True):
        new_queryword = constants.Lyhendid.get_value_by_name(query_string).decode('utf-8')
        querywords.update([new_queryword])
      if query_string in constants.Lyhendid.get_constant_values(uppercase=True):
        new_queryword = constants.Lyhendid.get_name_by_value(query_string, uppercase=True).decode('utf-8')
        querywords.update([new_queryword])
      categories = json_data['categories']
      action = json_data['action']

    except Exception, e:  # TODO! don't even need this here
      logging.error(e)
      self.response.out.write('{}')
    
    search_results = []
    search_results1 = []

    for cat in categories:
      
      if action == 'archive_search':
        date_algus = json_data.get('date_algus') if json_data.get('date_algus') else '2014-01-01'
        search_results1 = search_archive(querywords, cat, date_algus)

      elif action == 'list_search':
        search_results1 = list_search(querywords,cat)

      elif action == 'search':
        date_algus = '2014-01-01'
        print "category is ", repr(cat)
        search_results1 = do_search(querywords,cat,date_algus)

      elif action == 'custom_search':
        date_algus = '2014-01-01'
        search_results1 = custom_search(querywords,cat,date_algus,email)

      elif action=='landing_search':
        date_algus = '2014-01-01'        
        if cat in ['EU Sanctions', 'OFAC Sanctions']:
          search_results_1 = list_search(querywords,cat)
          if search_results_1:
            for result in search_results_1:
              params = {'programs': result['programs'],
                        'name': result['name']
                        }
              search_results.append(params)
              
        elif cat not in ['EU Sanctions', 'OFAC Sanctions']:
          search_results_1 = do_search(querywords,cat,date_algus)
          if search_results_1:
            for result in search_results_1:
              params = {'result_link': result[0],
                        'result_title': result[1],
                        'result_date': result[2],
                        'queryword': result[3],
                        'categories': result[4]
                        }
              search_results.append(params)
      
      # There are different result set structures for different search types
      if search_results1 and action != 'list_search':  # we don't want to add empty values to our final search list
        for result in search_results1:
          params = {'result_link': result[0],
                    'result_title': result[1],
                    'result_date': result[2],
                    'queryword': result[3],
                    'categories': result[4]
                    }
          search_results.append(params)
      
      if search_results1 and action=='list_search': # we don't want to add empty values to our final search list
        for result in search_results1:
          params = {'programs': result['programs'],
                    'name': result['name']
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
        if custom.category_type == 'rss_source' and category == custom.category_name:
          try:
            search_results.extend(rss_parse.parse_feed(querywords, category, date_algus))
            #print search_results
          except Exception, e:
            logging.error('failed with custom rss source')
            #message = 'Could not find querywords "%s" from category "%s"' % (repr(querywords), repr(category))
            #logging.error(message)
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
            #message = 'Could not find querywords "%s" from category "%s"' % (repr(querywords), repr(category))
            #logging.error(message)
            logging.error(e)
            pass

    return search_results  # link, title, date, qword, category


def search_archive(querywords, category, date_algus='2014-01-01'):
    """ Searches from archives and registries. """
    search_results = []
    search_list = [
        {'category': 'Politsei uudiste arhiiv', 'results': politsei_parse.search_politsei},  # test if two same names work in front
        {'category': 'Maa- ja ringkonnakohtu lahendid ', 'results': riigiteataja_parse.search_kohtu},  # leht tihti maas
        {'category': 'Riigikohtu lahendite arhiiv', 'results': riigikohtu_parse.search_kohtu},  # test if two same names work in front
        {'category': 'Meedia', 'results': archive_search.search_media},
        {'category': 'Eur-Lex', 'results': eurlex_parse.search_eurlex},
        {'category': u'Eelnõude otsing', 'results': riigiteataja_parse.search_eelnou},
        ]
        
    for source in search_list:
      # Otsime meedia arhiividest
      if source['category'] == 'Meedia':  # mitu allikat
        if category in [x[0] for x in archive_search.categories]:  # mitu allikat
          search_results.extend(source['results'](querywords, category, date_algus))

      # Everything else 
      if category == source['category']:
        # logging.error(date_algus) # TODO! Reformat date
        search_results.extend(source['results'](querywords, category, date_algus))
        
    return search_results  # link, title, date, qword, category
    
    
def do_search(querywords, category, date_algus):
  """ Meant to be used for monitoring news and updates. """
  search_results=[]

  search_list = [
    {'category': 'Politsei uudised', 'results': politsei_parse.search_politsei},
    {'category': 'Riigiteataja uudised', 'results': riigiteataja_parse.search_riigiteataja_uudised},
    {'category': 'oigusaktid', 'results': riigiteataja_parse.search_oigusaktid},
    {'category': 'RSS allikad', 'results': rss_parse.parse_feed},
    {'category': 'ministeeriumid', 'results': ministry_parse.search_ministry},
    {'category': 'Ametlikud teadaanded', 'results': riigiteataja_parse.search_ametlikud_teadaanded},
    {'category': 'Riigiteataja seadused', 'results': riigiteataja_parse.search_seadused},
    {'category': 'Maa- ja ringkonnakohtu lahendid', 'results': riigiteataja_parse.search_kohtu},  # to avoid duplicates, add space to source

    {'category': 'finantsinspektsioon', 'results': fi_parse.search_EU_supervision},
    {'category': 'FI juhendid', 'results': fi_parse.search_fi},

    # advokaadibürood (need, mida mainitud pole, on RSS allikate all)
    {'category': u'Advokaadi- ja õigusbürood', 'results': LawfirmParsers.search_bureau},  # map async to tasklet

  ]

  for source in search_list:

    # Otsime finantsinspektsioonist
    if source['category'] == 'finantsinspektsioon':
      if category in [x[0] for x in fi_parse.categories]:
        search_results.extend(source['results'](querywords, category, date_algus))

    # Otsime FI juhenditest
    if source['category'] == 'FI juhendid':  # mitu allikat
      if category in ['FI juhendite projektid','FI kehtivad juhendid']:
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with FI juhendid')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass

    # Otsime ministeeriumitest (mis ei ole RSS)
    if source['category'] == 'ministeeriumid':
      if category in [x[0] for x in ministry_parse.categories]:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with ministeeriumid')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass

    # Otsime FI teadetest
    if source['category'] == 'FI teated':
      #if category in fi_parse.pages: # mitu allikat
      if category in [x[0] for x in fi_parse.categories]:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with FI teated')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass

    # Otsime riigi ja/või KOV õigusaktidest
    if source['category'] == 'oigusaktid':
      if category in [u'Kehtivate KOV õigusaktide otsing',u'Kehtivate õigusaktide otsing']:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with FI oigusaktid')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass

    # Otsime riigiteataja uudistest ( seadusuudised; kohtuuudised; õigusuudised )
    if source['category'] == 'Riigiteataja uudised':
      if category in riigiteataja_parse.categories_uudised:  # mitu allikat
        try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with riigiteataja uudised')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass

    # Otsime riigiteataja seadustest
    if source['category'] == 'Riigiteataja seadused':
      if category in riigiteataja_parse.categories_seadused:
        try:
          logging.error("in riigiteataja seadused")
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with riigiteataja seadused')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass

    # Otsime RSS allikatest
    if source['category'] == 'RSS allikad':
      #catlist = [key for key, value in rss_parse.categories2] rss_parse.categories2
      if category in [x[0] for x in rss_parse.categories]:  # mitu allikat
        search_results.extend(source['results'](querywords, category, date_algus))
        """try:
          search_results.extend(source['results'](querywords, category, date_algus))
        except Exception, e:
          logging.error('failed with rss allikad')
          #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
          #logging.error(message)
          logging.error(e)
          pass"""

    # Everything else
    if category == source['category']:
      try:
        search_results.extend(source['results'](querywords, category, date_algus))
      except Exception, e:
        logging.error('failed with singular category search')
        #message = 'Could not find querywords "%s" from category "%s"' % (str(querywords),str(category))
        #logging.error(message)
        logging.error(e)
        pass
  #print search_results
  return search_results  # link, title, date, qword, category
 
 
def list_search(querywords,category):

  search_results=[]

  if category == 'OFAC Sanctions':
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
  
  if category == 'EU Sanctions':
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
  
  #print search_results
  return search_results
