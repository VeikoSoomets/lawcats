# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2017 Kaspar Gering
#
#
#

import sys

import functools

sys.path.insert(0, 'libs')

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path)

from google.appengine.api import search
from google.appengine.ext import deferred

import logging
from base_handler import BaseHandler


import models

from google.appengine.ext import ndb

from parsers.custom_source import *
from google.appengine.api import memcache
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(300)

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
    9: u"\u2079"
}


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


class AddLawIndex():

  @classmethod
  def delete_all_in_index(self):
    """Delete all the docs in the given index."""
    res = models.RiigiTeatajaMetainfo2.query().fetch()
    if not res:
        logging.error('did not get res, cannot delete index')
        return
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
      except Exception, e:
        logging.error(e)
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
    # Tokenize words for enhanced search capabilities from Search Index API
    def tokenize(phrase):
        a = []
        for word in phrase.split():
            j = 1
            if not word.isdigit() and word.isalnum():  # remove numbers and special chars
                while True:
                    for i in range(len(word) - j + 1):
                        token = word[i:i + j]
                        if len(token) > 3:  # NB! token limit 4
                            a.append(token)
                    if j == len(word):
                        break
                    j += 1
        return a

    def batch(iterable, n = 1):
       l = len(iterable)
       for ndx in range(0, l, n):
           yield iterable[ndx:min(ndx+n, l)]


    """ Get laws from datastore and put to search api index """
    # TODO! fetch in batches (might need to use cursors)
    laws = models.RiigiTeatajaURLs.query().fetch()  # models.RiigiTeatajaURLs.title=='Lennundusseadus'
    put_laws = 0
    for law in laws:
      para_titles = []
      documents = []
      dbp_metas = []
      src = law.text #.decode('utf-8')
      articles = bs4.BeautifulSoup(src, "html5lib", from_encoding='utf8')

      # We want to understand superscript styles and show them properly to avoid confusion in paragraph numbers
      try:
          for e in articles.findAll('sup'):

              try:
                part1 = [y for x, y in superscript_map.iteritems() if x == int(e.get_text()[0])][0]
              except Exception:
                pass

              try:
                part2 = [y for x, y in superscript_map.iteritems() if x == int(e.get_text()[1])][0]
              except Exception:
                pass

              try:
                  if len(e.get_text())==1:
                      e.string = part1
                  else:
                      e.string = part1 + part2
              except Exception:
                pass

      except Exception, e:
          logging.error(e)
          pass
      url_base = law.link

      #for article in articles:
      paragraph_title, article_link, law_title, content = None, None, None, None
      law_title = law.title
      # Get content
      content = articles.find_all('p')  #, attrs={'class': 'announcement-body'}
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
          para_token = ','.join(tokenize(paragraph_title))
          document = search.Document(
          fields=[
             search.AtomField(name='law_title', value=law_title),
             search.AtomField(name='law_link', value=article_link),
             search.NumberField(name='para_nbr', value=int(para_nbr)),
             search.TextField(name='para_title', value=paragraph_title),
             search.TextField(name='para_token', value=para_token),
             search.TextField(name='content', value=content)
             ])
          documents.append(document)

       # TODO! instead of str(list( , why not insert list?
      try:
          dbp_meta = models.RiigiTeatajaMetainfo(title=law_title, para_title=str(list(set(para_titles))) ) # set to remove duplicates, then repr of list for later parsing
          dbp_meta.put()
      except Exception, e:
          logging.error(e)
          pass

      # TODO! truncate to < 100bytes so you'd get all laws (currently a couple missing)
      try:  # try is only here because "Euroopa Parlamendi ja n├Ąukogu m├ż├żruse (E├£) nr 1082/2006 ┬½Euroopa territoriaalse koost├Č├Č r├╝hmituse (ETKR) kohta┬╗ rakendamise seadus" is exceeds 100byte limit for index name
        """ Put documents to index in a batch (limit is 200 in one batch). Each separate law to spearata index. """
        for x in batch(documents, 200):
            try: # TODO! fix index names
                index = search.Index(name=law_title.encode('ascii', 'ignore').replace(' ','')[:76])  # index name must be printable ASCII
                index.put(x)
            except Exception:
                pass
      except Exception, e:
        logging.error(e)
        # pass only because sometimes index name exceed 100byte limit, but we don't care for those atm
        pass

      put_laws += 1


      dbp_meta = models.RiigiTeatajaMetainfo(title=law_title, para_title=str(list(set(para_titles))) ) # set to remove duplicates, then repr of list for later parsing
      dbp_metas.append(dbp_meta)

    logging.error('put %s laws to index!' % str(put_laws))

    try:
        for future in batch(dbp_metas, 200):
            try: # TODO! fix index names
                ndb.put_async(future)
            except Exception:
                pass
    except Exception, e:
        logging.error(e)
        pass
    logging.error('successfully put metas!')

    future = ndb.put_multi_async(dbp_metas)
    ndb.Future.wait_all(future)
    #deferred.defer(get)


class RiigiTeatajaDownloadHandler():

  @classmethod
  def get_urls(self):
    urllist = []
    src = urllib2.urlopen('https://www.riigiteataja.ee/lyhendid.html', timeout=60)
    soup = bs4.BeautifulSoup(src,  "html5lib")
    soup = soup.find('tbody')
    for result in soup.findAll('tr'):
      law = result.findAll('td')[0]
      link = law.findNext('a', href=True).get('href')
      title = law.findNext('a', href=True).get_text()
      url = "https://www.riigiteataja.ee/%s?leiaKehtiv" % link
      urllist.append({'title': title, 'url': url})
    src.close()
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
      try:
          models.RiigiTeatajaURLs.query().map(self.delete_async_)
      except Exception, e:
          logging.error(e)
          pass
      try:
          models.RiigiTeatajaMetainfo.query().map(self.delete_async_)
      except Exception, e:
          logging.error(e)
          pass
      try:
          models.RiigiTeatajaMetainfo2.query().map(self.delete_async_)
      except Exception, e:
          logging.error(e)
          pass


  @classmethod
  def get(self):
      # TODO! do in batches, make multiple tasks, so each task would run less than 10min
      urls = self.get_urls()
      logging.error(len(urls))

      dbp_metas = []
      dbps = []

      def handle_result(rpc, url):
          result = rpc.get_result()
          soup = bs4.BeautifulSoup(result.content, "html5lib")
          law = soup.find('div', attrs={'id': 'article-content'}).encode('utf-8')
          dbp = models.RiigiTeatajaURLs(title=url['title'], link=url['url'], text=law)
          dbps.append(dbp)  # dbp.put()
          dbp_meta = models.RiigiTeatajaMetainfo2(title=url['title'])
          dbp_metas.append(dbp_meta)  # dbp_meta.put()

      rpcs = []
      for url in urls:
          rpc = urlfetch.create_rpc()
          rpc.callback = functools.partial(handle_result, rpc, url)
          urlfetch.make_fetch_call(rpc, url['url'])
          rpcs.append(rpc)

      for rpc in rpcs:
          rpc.wait()

      future = ndb.put_multi_async(dbps)
      future2 = ndb.put_multi_async(dbp_metas)
      ndb.Future.wait_all(future)
      ndb.Future.wait_all(future2)

  #deferred.defer(get)



class DataGatherer(BaseHandler):
  """ Gets data from web and puts to Datastore. Uses "deferred" module, which uses queues.
    Good for long-running tasks """

  @classmethod
  def get(self):
    try:
        RiigiTeatajaDownloadHandler.delete_htmls()
    except Exception, e:
        logging.error(e)
        pass

    try:
        deferred.defer(RiigiTeatajaDownloadHandler.get)
        #RiigiTeatajaDownloadHandler.get()
    except Exception, e:
        logging.error(e)
        pass

class DataIndexer(BaseHandler):
  """ Gets data from web and puts to Datastore. Uses "deferred" module, which uses queues.
    Good for long-running tasks """

  @classmethod
  def get(self):
    try:
        AddLawIndex.delete_all_in_index()
    except Exception, e:
        logging.error(e)
        pass

    try:
        deferred.defer(AddLawIndex.get)
        #AddLawIndex.get()
    except Exception, e:
        logging.error(e)
        pass

#deferred.defer(DataGatherer.get)

