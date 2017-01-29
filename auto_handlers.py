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


class AddLawIndex(BaseHandler):

  @classmethod
  def delete_all_in_index(self,index_name):
    """Delete all the docs in the given index."""
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

  def get(self):
    self.delete_all_in_index('laws')  # empty index before reindexing

    def batch(iterable, n = 1):
       l = len(iterable)
       for ndx in range(0, l, n):
           yield iterable[ndx:min(ndx+n, l)]

    """ Get laws from datastore and put to search api index """
    laws = models.RiigiTeatajaURLs.query().fetch()
    put_laws = 0
    for law in laws:
      documents = []
      src = law.text
      soup = bs4.BeautifulSoup(src, "html5lib")
      url_base = law.link

      # Get individual articles
      articles = soup.find_all('div', attrs={'id': 'article-content'})
      for article in articles:
        article_link, law_title, content = None, None, None
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
          if (c.find_previous_sibling('h3') and c.find_previous_sibling('h3').find_next('strong')):
              paragraph = c.find_previous_sibling('h3').find_next('strong').contents[0]
              paragraph_title = c.find_previous_sibling('h3').get_text()

          try:
            para_nbr = paragraph.split()[1].replace('.','').replace(' ','')
          except Exception:
            pass
          content = c.get_text()

          # build document
          if article_link:  # lets prune some crappy entries we don't need
            document = search.Document(
            fields=[
               search.AtomField(name='law_title', value=law_title),
               search.AtomField(name='law_link', value=article_link),
               search.NumberField(name='para_nbr', value=int(para_nbr)),
               search.TextField(name='para_title', value=paragraph_title),
               search.TextField(name='content', value=content)
               ])
            documents.append(document)

      try:  # try is only here because "Euroopa Parlamendi ja n├Ąukogu m├ż├żruse (E├£) nr 1082/2006 ┬½Euroopa territoriaalse koost├Č├Č r├╝hmituse (ETKR) kohta┬╗ rakendamise seadus" is exceeds 100byte limit for index name

        self.delete_all_in_index(law_title.encode('ascii', 'ignore').replace(' ',''))  # empty index before reindexing
        """ Put documents to index in a batch (limit is 200 in one batch). Each separate law to spearata index. """
        for x in batch(documents, 200):
            index = search.Index(name=law_title.encode('ascii', 'ignore').replace(' ',''))  # index name must be printable ASCII
            index.put(x)
      except Exception, e:
        # pass only because sometimes index name exceed 100byte limit, but we don't care for those atm
        pass

      put_laws += 1

    logging.error('put %s laws to index!' % str(put_laws))


class AutoAddSource(BaseHandler):
  """ Tries to automatically add a user requested source. If fails, notifies admin that there are open requests. """

  def get(self):
    start_time = time.time()
    datelimit=datetime.datetime.now().date()

    user_list = [x.email_address for x in models.User.query(models.User.usage_expire_date>=datelimit,projection=['email_address']).fetch()] # only take users who don't have expired usage
    datastore_results = models.SourceRequest.query(ndb.AND(models.SourceRequest.user_id.IN(user_list),models.SourceRequest.implemented_dtime==None)).fetch() # find a way to make this more optimal
    crawled_keys=[]
    data = [p.to_dict() for p in datastore_results]  # put individual datastore results to dictionary

    for line in data:
      if not line['implemented_dtime']:
        # Start implementing
        implemented, resolution = do_implement(line['url'], line['user_id'])
        if implemented:
          crawled_keys.append(line['key'])
          msg = 'implemented ' + line['url']
          logging.error(msg)
        else:
          msg = 'did not implement ' + line['url']
          logging.error(msg)

    """ Update last crawl date async """
    for key in crawled_keys:
      qry = models.SourceRequest.add_implemented_dtime(key)
      qry.get_result()

    #ndb.Future.wait_all(futures) # don't even have to wait for when updating is done  """

    #except Exception, e:
    #logging.error(e)

    message = str(len(crawled_keys)) + ' new custom sources implementation took ' + str(time.time() - start_time) + ' seconds. Failed to implement ' + str(len(data)-len(crawled_keys)) + ' sources.'
    logging.error(message)
    implemented = False
    if len(crawled_keys)>0:
      implemented = True

    return implemented
    #self.render_template('admin.html',{'message_type':'success','message':message})


from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(600)
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
      models.RiigiTeatajaMetainfo.query().map(self.delete_async_)


  @classmethod
  def get(self):
      urls = self.get_urls()
      dbps_meta = []
      dbps_main = []
      for url in urls:
        text = urlfetch.fetch(url['url'], method=urlfetch.GET)
        dbp = models.RiigiTeatajaURLs(title=url['title'], link=url['url'], text=text.content)
        dbp_meta = models.RiigiTeatajaMetainfo(title=url['title'])
        dbps_main.append(dbp)
        dbps_meta.append(dbp_meta)

      future = ndb.put_multi_async(dbps_main)
      future_meta = ndb.put_multi_async(dbps_meta)
      ndb.Future.wait_all(future_meta)
      ndb.Future.wait_all(future)


from google.appengine.ext import deferred
class DataGatherer(BaseHandler):
  """ Gets data from web and puts to Datastore. Uses "deferred" module, which uses queues.
    Good for long-running tasks """
  def get(self):
    RiigiTeatajaDownloadHandler.delete_htmls()
    deferred.defer(RiigiTeatajaDownloadHandler.get)
    return

def do_implement(link,user_id):
    # do implementation
    implemented = False
    resolution = False
    # make sure to add http:// when it is not there
    if not link.startswith( 'http:', 0, 5):
        link = 'http://' + link

    try:
      # Try if rss handler works
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

    try:
      # src = urllib2.urlopen(link)
      # Try if blogs_handler will work
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
