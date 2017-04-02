import urllib2

import bs4
from google.appengine.api import memcache

import models
from google.appengine.ext import ndb
from constants import Categories, Abbreviations


class CategoryService():

  @classmethod
  def generate(cls):
    dbps = []

    def create_model_instances(dbps, category, level, parent_category_key=None, link=None, lang=None):
      category_id = ndb.Model.allocate_ids(size=1, parent=parent_category_key)[0]
      category_key = ndb.Key('Category', category_id, parent=parent_category_key)
      dbp = models.Category(name=category.name, level=level, key=category_key, link=link, lang=lang)
      dbps.append(dbp)
      if category.child_constants:
        level += 1
        for sub_category in category.child_constants:
          create_model_instances(dbps, sub_category, level, category_key, link=sub_category.values.get('link'),
                                 lang=sub_category.values.get('lang'))

    for main_category in Categories.get_constants():
      create_model_instances(dbps, main_category, 1)
    ndb.put_multi(dbps)
    return {'message_type': 'success', 'nr_of_generated_instances': len(dbps)}

  @classmethod
  def get(cls, email=None):
    cat_mem_name = email.encode('ascii', 'ignore').replace('.', '').replace('@', '')
    categories = memcache.get(cat_mem_name + 'Categories')
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
      memcache.set(cat_mem_name + 'Categories', categories)
    return categories

  @classmethod
  def erase(cls):
    categories = models.Category.query().fetch(keys_only=True)
    ndb.delete_multi(categories)


class HTMLDownloaderService():

  @classmethod
  def riigiteataja_generate(cls):
    dbps = []

    def get_urls():
      urllist = []
      src = urllib2.urlopen('https://www.riigiteataja.ee/lyhendid.html', timeout=60)
      soup = bs4.BeautifulSoup(src, "html5lib")
      soup = soup.find('tbody')
      for result in soup.findAll('tr'):
        law = result.findAll('td')[0]
        link = law.findNext('a', href=True).get('href')
        title = law.findNext('a', href=True).get_text()
        url = "https://www.riigiteataja.ee/%s?leiaKehtiv" % link
        urllist.append({'title': title, 'url': url})
      src.close()
      return urllist

    urls = get_urls()
    for url in urls:
      src = urllib2.urlopen(url['url'], timeout=10)
      soup = bs4.BeautifulSoup(src, "html5lib")
      law = soup.find('div', attrs={'id': 'article-content'}).encode('utf-8')
      dbp = models.RiigiTeatajaURLs(title=url['title'], link=url['url'], text=law)
      dbps.append(dbp)
    ndb.put_multi(dbps)
    return {'message_type': 'success', 'nr_of_generated_instances': len(dbps)}

  @classmethod
  def erase(cls):
    riigiTeatajaURLs = models.RiigiTeatajaURLs.query().fetch(keys_only=True)
    ndb.delete_multi(riigiTeatajaURLs)


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
  def search(cls, querywords, categories, date_start):
    search_results = []

    search_list = [
      {'category': 'RSS allikad', 'results': rss_parse.parse_feed},
      {'category': 'ministeeriumid', 'results': ministry_parse.search_ministry},
      {'category': 'Riigiteataja seadused', 'results': riigiteataja_parse.search_seadused},
      {'category': u'Õigusaktide otsing', 'results': riigiteataja_parse.search_oigusaktid},
      {'category': 'Maa- ja ringkonnakohtu lahendid', 'results': riigiteataja_parse.search_kohtu},
      # to avoid duplicates, add space to source

      {'category': 'Eur-Lex eestikeelsete dokumentide otsing', 'results': eurlex_parse.search_eurlex},

      # advokaadibürood (need, mida mainitud pole, on RSS allikate all)
      {'category': u'Advokaadi- ja õigusbürood', 'results': LawfirmParsers.search_bureau},  # map async to tasklet

    ]

    # for source in search_list:
    #
    #   # Otsime ministeeriumitest (mis ei ole RSS)
    #   if source['category'] == 'ministeeriumid':
    #     if category in [x[0] for x in ministry_parse.categories]:  # mitu allikat
    #       try:
    #         search_results.extend(source['results'](querywords, category, date_algus))
    #       except Exception, e:
    #         logging.error('failed with ministeeriumid')
    #         logging.error(e)
    #         pass
    #
    #   # Otsime riigi ja/või KOV õigusaktidest
    #   if source['category'] == 'oigusaktid':
    #     if category in [u'Kehtivate KOV õigusaktide otsing', u'Õigusaktide otsing']:  # mitu allikat
    #       try:
    #         search_results.extend(source['results'](querywords, category, date_algus))
    #       except Exception, e:
    #         logging.error('failed with FI oigusaktid')
    #         logging.error(e)
    #         pass
    #
    #   # Otsime riigiteataja uudistest ( seadusuudised; kohtuuudised; õigusuudised )
    #   if source['category'] == 'Riigiteataja uudised':
    #     if category in riigiteataja_parse.categories_uudised:  # mitu allikat
    #       try:
    #         search_results.extend(source['results'](querywords, category, date_algus))
    #       except Exception, e:
    #         logging.error('failed with riigiteataja uudised')
    #         logging.error(e)
    #         pass
    #
    #   # Otsime RSS allikatest
    #   if source['category'] == 'RSS allikad':
    #     # catlist = [key for key, value in rss_parse.categories2] rss_parse.categories2
    #     if category in [x[0] for x in rss_parse.categories]:  # mitu allikat
    #       search_results.extend(source['results'](querywords, category, date_algus))
    #
    #   # Everything else
    #   if category == source['category']:
    #     search_results.extend(source['results'](querywords, category, date_algus))
    #     try:
    #       search_results.extend(source['results'](querywords, category, date_algus))
    #     except Exception, e:
    #       logging.error('failed with singular category search')
    #       logging.error(e)
    #       pass
    #
    # # Make results unique (if there are overlaps from multiple sources, eg. "Õigusaktide otsing" source
    # search_results = [list(x) for x in set(tuple(x) for x in search_results)]
    #
    # # TODO! Sort results by date
    # # search_results = search_results.sort(key=lambda r: r[2])
    #
    # # Sort results by rank (if there is rank)
    # try:
    #   search_results = sorted(search_results, key=itemgetter(5), reverse=True)  # TODO! fix
    # except Exception:
    #   pass

    return search_results  # link, title, date, qword, category, rank
