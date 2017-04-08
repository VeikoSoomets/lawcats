# -*- coding: utf-8 -*-
import logging
import urllib2
from operator import itemgetter

import bs4
import functools
from google.appengine.api import memcache, urlfetch

import models
from google.appengine.ext import ndb
from constants import Categories, Abbreviations


class CategoryService():

  @classmethod
  def generate(cls):
    category_models = []

    def create_category_instances(category, level, parent_category_key=None, link=None, lang=None):
      category_id = ndb.Model.allocate_ids(size=1, parent=parent_category_key)[0]
      category_key = ndb.Key('Category', category_id, parent=parent_category_key)
      category_model = models.Category(name=category.name, level=level, key=category_key, link=link, lang=lang)
      category_models.append(category_model)
      if category.child_constants:
        level += 1
        for sub_category in category.child_constants:
          create_category_instances(sub_category, level, category_key, link=sub_category.values.get('link'),
                                 lang=sub_category.values.get('lang'))

    for main_category in Categories.get_constants():
      create_category_instances(main_category, 1)
    ndb.put_multi(category_models)
    return {'message_type': 'success', 'nr_of_generated_instances': len(category_models)}

  @classmethod
  def get(cls, email=None):
    catergory_memcache_name = email.encode('ascii', 'ignore').replace('.', '').replace('@', '')
    categories = memcache.get(catergory_memcache_name + 'Categories')
    if not categories:
      categories = []
      main_categories = models.Category.query(models.Category.level == 1).fetch()
      for main_category in main_categories:
        category = {'name': main_category.name, 'sub_categories': []}
        sub_categories = models.Category.query(ancestor=main_category.key).filter(models.Category.level==2).fetch()
        for sub_category in sub_categories:
          child_categories = []
          children = models.Category.query(ancestor=sub_category.key).filter(models.Category.level==3).fetch()
          for child in children:
            child_categories.append({'name': child.name, 'link': child.link, 'lang': child.lang})
          category['sub_categories'].append({'name': sub_category.name, 'child_categories': child_categories})
        categories.append(category)

      if email:
        custom_categories = []
        custom_child_categories = []
        datastore_custom_cats = models.CustomCategory.query(models.CustomCategory.user_id == email).fetch()
        if datastore_custom_cats:
          data = [p.to_dict() for p in datastore_custom_cats]
          for line in data:
            custom_child_categories.append({'link': line['nice_link'], 'name': line['category_name']})
          custom_categories.append({'name': 'Custom', 'sub_categories': [{'name': 'Custom Sources',
                                                                          'child_categories': custom_child_categories}]})
          categories.extend(custom_categories)
      memcache.set(catergory_memcache_name + 'Categories', categories)
    return categories

  @classmethod
  def erase(cls):
    categories = models.Category.query().fetch(keys_only=True)
    ndb.delete_multi(categories)


class SearchService():

  @classmethod
  def get_querywords(cls, query):
    query = query.encode('utf-8')
    querywords = set(query.split(' '))
    query = query.upper()
    for abbrevation in Abbreviations.get_constants():
      long_name = abbrevation.values.get('long_name')
      if query in abbrevation.name.upper():
        querywords.update([long_name])
      elif query in long_name.upper():
        querywords.update([abbrevation.name])
    return querywords

  @classmethod
  def search(cls, query_words, search_category, date_start):
    search_results = []
    search_category = search_category.encode('utf-8')

    for main_category in Categories.EESTI.child_constants:
      for category in main_category.child_constants:
        if search_category == category.name:
          try:
            search_results.extend(category.values.get('search_function')(query_words, category, date_start))
          except Exception, e:
            logging.error("Search from category %s failed with error % " (category.name, e.message))
            pass

    search_results = [list(x) for x in set(tuple(x) for x in search_results)]

    # TODO! Sort results by date

    # Sort results by rank (if there is rank)
    try:
      search_results = sorted(search_results, key=itemgetter(5), reverse=True)  # TODO! fix
    except Exception:
      pass

    return search_results  # link, title, date, qword, category, rank


class LawService():
  RIIGITEATAJA_SRC_URL = 'https://www.riigiteataja.ee/lyhendid.html'
  RIIGITEATAJA_LAW_BASE_URL = 'https://www.riigiteataja.ee/%s?leiaKehtiv'

  @classmethod
  def generate_laws(cls):
    batch_max_size = 50

    def get_urls():
      urllist = []
      src = urllib2.urlopen(cls.RIIGITEATAJA_SRC_URL, timeout=60)
      soup = bs4.BeautifulSoup(src, "html5lib")
      soup = soup.find('tbody')
      for result in soup.findAll('tr'):
        law = result.findAll('td')[0]
        link = law.findNext('a', href=True).get('href')
        title = law.findNext('a', href=True).get_text()
        url = cls.RIIGITEATAJA_LAW_BASE_URL % link
        urllist.append({'title': title, 'url': url})
      src.close()
      return urllist

    def batch(iterable, n=1):
      l = len(iterable)
      for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

    @ndb.tasklet
    def fetch_url(url):
      result = yield ndb.get_context().urlfetch(url['url'])
      if result.status_code == 200:
        raise ndb.Return({'url':url, 'response':result.content})

    @ndb.tasklet
    def generate_law(url, url_response):
      soup = bs4.BeautifulSoup(url_response, "html5lib")
      law_html = soup.find('div', attrs={'id': 'article-content'}).encode('utf-8')
      law_id = ndb.Model.allocate_ids(size=1)[0]
      law_key = ndb.Key('Law', law_id)
      law_model_key = yield models.Law(title=url['title'], link=url['url'], text=law_html, key=law_key).put_async()
      raise ndb.Return({'key': law_model_key, 'title': url['title'], 'link': url['url'], 'text': law_html})

    @ndb.tasklet
    def persist_law_metainfo(law, paragraph):
      law_metainfo_key = yield models.LawMetaInfo(paragraph_number=paragraph.get('number'), paragraph_link=paragraph.get('link'),
                               paragraph_title=paragraph.get('title'), paragraph_content=paragraph.get('content'),
                               parent=law.get('key')).put_async()
      raise ndb.Return(law_metainfo_key)

    def generate_law_metainfo(law):
      articles = bs4.BeautifulSoup(law.get('text'), "html5lib", from_encoding='utf8')
      paragraph_elements = articles.find_all('p')
      futures = []
      for paragraph_element in paragraph_elements:
        link_element = paragraph_element.find_next('a')
        if not link_element:
          continue
        paragraph_link = link_element.get('name')
        if paragraph_link:
          paragraph_link = law.get('link') + '#' + paragraph_link
        else:
          continue
        if paragraph_element.find_previous_sibling('h3') and paragraph_element.find_previous_sibling('h3').find_next(
                'strong'):
          paragraph = paragraph_element.find_previous_sibling('h3').find_next('strong').contents[0]
          paragraph_title = paragraph_element.find_previous_sibling('h3').get_text()
          paragraph_number = paragraph.split()[1].replace('.', '').replace(' ', '')
        else:
          continue
        paragraph_content = paragraph_element.get_text().encode('utf-8')
        paragraph = {
          'number': int(paragraph_number),
          'link': paragraph_link,
          'title': paragraph_title,
          'content': paragraph_content
        }
        futures.append(persist_law_metainfo(law, paragraph))
      return futures

    urls = get_urls()
    for url_batch in batch(urls, batch_max_size):
      fetch_futures = []
      law_futures = []
      law_metainfo_futures = []
      for url in url_batch:
        logging.info("Requesting source from URL with title %s" % (url.get('title')))
        fetch_future = fetch_url(url)
        fetch_futures.append(fetch_future)
      ndb.Future.wait_all(fetch_futures)
      for fetch_future in fetch_futures:
        future_result = fetch_future.get_result()
        logging.info("Generating new law for title %s" % (future_result.get('url').get('title')))
        law_future = generate_law(future_result.get('url'), future_result.get('response'))
        law_futures.append(law_future)
      ndb.Future.wait_all(law_futures)
      for law_future in law_futures:
        law_future_result = law_future.get_result()
        logging.info("Generating new metainfo for law %s" % (law_future_result.get('title')))
        law_metainfo_futures += generate_law_metainfo(law_future_result)
      ndb.Future.wait_all(law_metainfo_futures)
    logging.info("Batches completed")
    return {'message_type': 'success', 'nr_of_generated_instances': len(urls)}

  @classmethod
  def erase_laws(cls):
    laws = models.Law.query().fetch(keys_only=True)
    ndb.delete_multi(laws)

  @classmethod
  def erase_metainfo(cls):
    laws_metainfo = models.LawMetaInfo.query().fetch(keys_only=True)
    ndb.delete_multi_async(laws_metainfo)