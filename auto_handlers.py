# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 Kaspar Gering
#
#
#

""" Automatiseeritud otsing - viib läbi otsinguid vastavalt märksõnadele ning soovitud allikatele
"""
import sys
#import urllib2
sys.path.insert(0, 'libs')

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path)
import csv
from google.appengine.api import search
from google.appengine.ext import deferred

import logging
#from google.appengine.ext.webapp.util import run_wsgi_app

from base_handler import BaseHandler

import base_handler

import handlers
import models

import datetime
import time

#from google.appengine.api import users
#from google.appengine.ext.deferred import defer
from google.appengine.ext import ndb

from parsers.custom_source import *
from google.appengine.api import memcache
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(600)


def datetime_object(date):
    """ Make dates ready for inserting into datastore Add new formats if needed. """
    try:
        date=datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        date = None  # if no date, then insert None; datetime.datetime.now().date()
    return date


class DeleteLastCrawl(BaseHandler):

  def get(self):
    self.wipe_datastore()

  @classmethod
  @ndb.tasklet
  def delete_async_(self, input_object):
    #key = ndb.Key('UserRequest', input_key.id())
    """preferred_lang=models.User.query(models.User.email_address==fuser).get()
    preferred_lang.preferred_lang=lang
    preferred_lang.put()"""
    last_crawl = datetime.datetime(2012,12,15,10,14,51,1)
    input_object.last_crawl = last_crawl
    del_future = yield input_object.put_async(use_memcache=False)
    raise ndb.Return(del_future)

  def wipe_datastore(self):
    users = models.UserRequest.query().map(self.delete_async_)
    self.render_template('admin.html',{'message_type':'success','message':'Operation successful, deleted last crawl dates!'})


class DeleteRequests(BaseHandler):

  def get(self):
    self.wipe_datastore()

  @classmethod
  @ndb.tasklet
  def delete_async_(self, input_object):
    #key = ndb.Key('UserRequest', input_key.id())
    key = input_object.key
    del_future = yield key.delete_async(use_memcache=False) # faster
    raise ndb.Return(del_future)

  def wipe_datastore(self):
    users = models.UserRequest.query().map(self.delete_async_)
    #users.get_result()
    """for t in [users]:#, profiles, tokens, sessions]:
        for i in t:
            i.key.delete_async() """
    users = models.UserRequest.query().fetch()
    if not users:
      self.render_template('sys.html',{'message_type':'success','message':'Operation successful, deleted requests async!'})
    else:
      self.render_template('sys.html',{'message_type':'danger','message':'Failed!'})


class DeleteCategories(BaseHandler):

  def get(self):
    self.wipe_datastore()

  @classmethod
  @ndb.tasklet
  def delete_async_(self, input_object):
    #key = ndb.Key('UserRequest', input_key.id())
    key = input_object.key
    del_future = yield key.delete_async(use_memcache=False) # faster
    raise ndb.Return(del_future)

  def wipe_datastore(self):
    cat = models.Category.query().map(self.delete_async_)
    maincat = models.MainCategories.query().map(self.delete_async_)
    subcat = models.SubCategories.query().map(self.delete_async_)

    self.render_template('sys.html',{'message_type':'success','message':'Operation successful, deleted all maincats, subcats and childcats!'})


class DeleteUserResults(BaseHandler):

  def get(self):
    self.wipe_datastore()

  @classmethod
  @ndb.tasklet
  def delete_async_(self, input_object):
    #key = ndb.Key('UserRequest', input_key.id())
    key = input_object.key
    del_future = yield key.delete_async(use_memcache=False) # faster
    raise ndb.Return(del_future)

  def wipe_datastore(self):
    users = models.UserResult.query().map(self.delete_async_)

    users = models.UserResult.query().fetch(1)
    if not users:
      self.render_template('sys.html',{'message_type':'success','message':'Operation successful, deleted all userresults async!'})
    else:
      self.render_template('sys.html',{'message_type':'danger','message':'Failed!'})

superscript_map = {
    0: u"\u2070",
    1: u"\u00B9",
    2: u"\u00B2",
    3: u"\u00B3",
    4: u"\u2074",
    5: u"\u2075",
    6: u"\u2076",
    7: u"\u2077",
    8: u"\u2078",
    9: u"\u2079",
    10: u"\u00B9\u2070",
    11: u"\u00B9\u00B9",
    12: u"\u00B9\u00B2",
    13: u"\u00B9\u00B3",
    14: u"\u00B9\u2074"
}


class AddLawIndex(BaseHandler):

  @classmethod
  def delete_all_in_index(self):
    """Delete all the docs in the given index."""
    res = models.RiigiTeatajaMetainfo2.query().fetch()
    for law in res:
      try:
        index_name = law.title.encode('ascii', 'ignore').replace(' ','')[:76]
        doc_index = search.Index(name=index_name)

        # looping because get_range by default returns up to 100 documents at a time
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id
                            for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            doc_index.delete(document_ids)
      except Exception:
        pass #  index name can't be more than 100 bytes

  @classmethod
  @ndb.tasklet
  def delete_async_(self, input_object):
      # key = ndb.Key('UserRequest', input_key.id())
      key = input_object.key
      del_future = yield key.delete_async(use_memcache=False)  # faster
      raise ndb.Return(del_future)

  @classmethod
  def get(self):


    def batch(iterable, n = 1):
       l = len(iterable)
       for ndx in range(0, l, n):
           yield iterable[ndx:min(ndx+n, l)]


    """ Get laws from datastore and put to search api index """
    laws = models.RiigiTeatajaURLs.query().fetch()
    put_laws = 0
    dbp_metas = []
    para_titles = []
    for law in laws:

      documents = []
      meta_docs = []
      src = law.text
      soup = bs4.BeautifulSoup(src, "html5lib")

      # we want to understand superscript styles and show them properly to avoid confusion in paragraph numbers
      try:
          for e in soup.findAll('sup'):
              e.string = [y for x, y in superscript_map.iteritems() if x == int(e.get_text())][0]
      except Exception:
          pass
      url_base = law.link

      # Get individual articles
      articles = soup.find_all('div', attrs={'id': 'article-content'})
      for article in articles:
        paragraph_title, article_link, law_title, content = None, None, None, None
        law_title = law.title
        # Get content
        content = article.find_all('p')  #, attrs={'class': 'announcement-body'}
        for c in content:
          try:
            article_link = c.find_next('a').get('name')
            article_link = url_base + '#' + article_link
          except:
            pass

          para_nbr = 0
          try:
            if (c.find_previous_sibling('h3') and c.find_previous_sibling('h3').find_next('strong')):
                paragraph = c.find_previous_sibling('h3').find_next('strong').contents[0]
                paragraph_title = c.find_previous_sibling('h3').get_text()
          except Exception:
            pass

          try:
            para_nbr = paragraph.split()[1].replace('.','').replace(' ','')

          except Exception:
            pass
          content = c.get_text()

          # build document
          if article_link and paragraph_title and para_nbr:  # lets prune some crappy entries we don't need
            para_titles.append(paragraph_title)

            document = search.Document(
            fields=[
               search.AtomField(name='law_title', value=law_title),
               search.AtomField(name='law_link', value=article_link),
               search.NumberField(name='para_nbr', value=int(para_nbr)),
               search.TextField(name='para_title', value=paragraph_title),
               search.TextField(name='content', value=content)
               ])


      # TODO! instead of str(list( , why not insert list?
      dbp_meta = models.RiigiTeatajaMetainfo(title=law_title, para_title=str(list(set(para_titles))) ) # set to remove duplicates, then repr of list for later parsing
      dbp_metas.append(dbp_meta)

      # TODO! truncate to < 100bytes so you'd get all laws (currently a couple missing)
      try:  # try is only here because "Euroopa Parlamendi ja n├Ąukogu m├ż├żruse (E├£) nr 1082/2006 ┬½Euroopa territoriaalse koost├Č├Č r├╝hmituse (ETKR) kohta┬╗ rakendamise seadus" is exceeds 100byte limit for index name
        """ Put documents to index in a batch (limit is 200 in one batch). Each separate law to spearata index. """
        for x in batch(documents, 200):
            index = search.Index(name=law_title.encode('ascii', 'ignore').replace(' ','1')[:76])  # index name must be printable ASCII
            index.put(x)
      except Exception, e:
        # pass only because sometimes index name exceed 100byte limit, but we don't care for those atm
        pass

      try:  # try is only here because "Euroopa Parlamendi ja n├Ąukogu m├ż├żruse (E├£) nr 1082/2006 ┬½Euroopa territoriaalse koost├Č├Č r├╝hmituse (ETKR) kohta┬╗ rakendamise seadus" is exceeds 100byte limit for index name
        """ Put documents to index in a batch (limit is 200 in one batch). Each separate law to spearata index. """
        for x in batch(meta_docs, 200):
            index = search.Index(name=law_title.encode('ascii', 'ignore').replace(' ','2')[:76])  # index name must be printable ASCII
            index.put(x)
      except Exception, e:
        # pass only because sometimes index name exceed 100byte limit, but we don't care for those atm
        pass

      put_laws += 1

    future_meta = ndb.put_multi_async(dbp_metas)
    ndb.Future.wait_all(future_meta)
    logging.error('put %s laws to index!' % str(put_laws))


class RiigiTeatajaDownloadHandler(BaseHandler):
  @classmethod
  def get_urls(self):
    src = urllib2.urlopen('https://www.riigiteataja.ee/lyhendid.html', timeout=600)
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


  @classmethod
  def delete_htmls(self):
      models.RiigiTeatajaURLs.query().map(self.delete_async_)
      models.RiigiTeatajaMetainfo2.query().map(self.delete_async_)
      models.RiigiTeatajaMetainfo.query().map(self.delete_async_)


  """@classmethod
  def delete_htmls2(self):
      models.RiigiTeatajaMetainfo.query().map(self.delete_async_)"""


  @classmethod
  def get(self):
      urls = self.get_urls()
      dbps_main = []
      dbps_meta = []
      for url in urls:
        text = urlfetch.fetch(url['url'], method=urlfetch.GET)
        dbp = models.RiigiTeatajaURLs(title=url['title'], link=url['url'], text=text.content)
        dbp_meta = models.RiigiTeatajaMetainfo2(title=url['title'])
        dbps_main.append(dbp)
        dbps_meta.append(dbp_meta)

      future = ndb.put_multi_async(dbps_main)
      future_meta = ndb.put_multi_async(dbps_meta)
      ndb.Future.wait_all(future)
      ndb.Future.wait_all(future_meta)


class DataGatherer(BaseHandler):
  """ Gets data from web and puts to Datastore. Uses "deferred" module, which uses queues.
    Good for long-running tasks """
  def get(self):
    RiigiTeatajaDownloadHandler.delete_htmls()
    deferred.defer(RiigiTeatajaDownloadHandler.get)
    return


class DataIndexer(BaseHandler):
  """ Indexes laws for faster access. Uses "deferred" module, which uses queues.
    Good for long-running tasks """
  def get(self):
    AddLawIndex.delete_all_in_index()
    deferred.defer(AddLawIndex.get)
    return


"""
class DataDeleter(BaseHandler):
  # just delete data
  def get(self):
    RiigiTeatajaDownloadHandler.delete_htmls2()
    return"""
