# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'libs')

import urllib2

from datetime import datetime as dt

import logging
from time import mktime
import bs4

import feedparser

from collections import defaultdict
import models
#from google.appengine.api import urlfetch
#urlfetch.set_default_fetch_deadline(45)

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

categories = [\
['Postimees','http://majandus24.postimees.ee/rss'], # majandus \
['Postimees','http://www.postimees.ee/rss/'],\
['Postimees','http://www.postimees.ee/rss/?r=128'], # kirmi \
['ERR','http://www.err.ee/rss'],\
[u'Õhtuleht','http://www.ohtuleht.ee/rss'],\
['raamatupidaja.ee','http://raamatupidaja.ee/RSS.aspx'],\
[u'Päevaleht','http://feeds.feedburner.com/eestipaevaleht?format=xml'],\
['Eesti Ekspress','http://feeds.feedburner.com/EestiEkspressFeed?format=xml'],\
['Maaleht','http://feeds.feedburner.com/maaleht?format=xml'],\
[u'Äripäev','http://www.aripaev.ee/rss'],\
['juura.ee','http://juura.ee/gw.php/news/aggregate/index/format/xml'],\
[u'Деловное Деломости','http://dv.ee/rss'],\
[u'МК-Эстония','http://www.mke.ee/index.php?option=com_k2&view=itemlist&format=feed&type=rss'],\
#[u'äripäev','http://feeds.feedburner.com/aripaev-rss'], # old, also has results, but lags behind\
# ############################ \
['BBC','http://feeds.bbci.co.uk/news/rss.xml?edition=us'],\
['BBC','http://feeds.bbci.co.uk/news/rss.xml?edition=int'],\
['BBC','http://feeds.bbci.co.uk/news/rss.xml?edition=uk'],\
['TIME','http://time.com/newsfeed/feed/'],\
['Forbes','http://www.forbes.com/real-time/feed2/'],\
['CNN','http://rss.cnn.com/rss/edition.rss'],\
['New York Times','http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'],\
['Reuters','http://feeds.reuters.com/reuters/businessNews?format=xml'],\
['The Economist','http://www.economist.com/sections/business-finance/rss.xml'],\
['Financial Times','http://www.ft.com/rss/home/uk'],\
['Business Insider','http://feeds2.feedburner.com/businessinsider'],\
['Bloomberg','http://www.bloombergview.com/rss'],\
['New York Post','http://nypost.com/feed/'],\
['The Guardian','http://www.theguardian.com/uk/rss'],\
['Forbes','http://www.forbes.com/real-time/feed2/'],\
['Deutche Welle','http://rss.dw.de/atom/rss-en-all'],\
['Helsingin Sanomat','http://www.helsinkitimes.fi/?format=feed&amp;type=rss'],\
['Wall Street Journal','http://online.wsj.com/xml/rss/3_7014.xml'],\
['Wall Street Journal','http://online.wsj.com/xml/rss/3_7455.xml'],\
['MarketWatch','http://feeds.marketwatch.com/marketwatch/topstories?format=xml'],\
['MarketWatch','http://feeds.marketwatch.com/marketwatch/financial/'],\
#['physorgtech','http://phys.org/rss-feed/technology-news/'],\
# ################################ \
['Riigihanked','https://riigihanked.riik.ee/register/rss/Teated.html'], # SSL certificate failed \
['Riigikohtu uudised','http://www.nc.ee/rss/?uudised=1'],\
['Riigiteataja ilmumas/ilmunud seadused','https://www.riigiteataja.ee/ilmunud_ilmumas.xml'], #uberslow, fix with handler!!!! \
['Riigikogu pressiteated', 'http://feeds.feedburner.com/RiigikoguPressiteated?format=xml'],\
['eurlex kohtuasjad', 'http://eur-lex.europa.eu/ET/display-feed.rss?rssId=163'], # NB! siin on võimalik keelt muuta\
['eurlex komisjoni ettepanekud', 'http://eur-lex.europa.eu/ET/display-feed.rss?rssId=161'],\
[u'eurlex parlament ja nõukogu', 'http://eur-lex.europa.eu/ET/display-feed.rss?rssId=162'],\
['Eversheds Ots & Co' , 'http://www.eversheds.com/code/RSS/Estonia/Estonia/News.xml'],\
['Eversheds Ots & Co' , 'http://www.eversheds.com/code/RSS/Estonia/Estonia/Article.xml'],\
['Lawin' , 'http://www.lawin.ee/ee/uudised/rss/'],\
['Redbaltic' , 'http://www.redbaltic.com/est/rss/'],\
['Sorainen' , 'http://www.sorainen.com/et/RSS/language/et/content_module/All'],\
['Varul' , 'http://www.varul.com/uudised/uudised.rss'],\
['Kaitseministeerium' , 'http://www.kaitseministeerium.ee/et/rss-uudiste-voog'],\
['Finantsministeerium' , 'http://www.fin.ee/rss_uudised'], \
# #################### \
 #['Majandusministeerium' , 'https://www.mkm.ee/et/news/all/feed'], ssl fail \
 #['haridusministeerium' , 'https://www.hm.ee/et/news/all/feed' ]# ssl certificate - not allowed \
 #['lextal' , 'http://www.lextal.ee/feed/' ] # doesn't work, has robots.txt \
['Hiljutised Riigikohtu lahendid','http://www.nc.ee/rss/?lahendid=1&tyyp=K'], # neid, mida muidu otsingust ei leia aga RSS'ist leiab, on dokument eemaldatud \
[u'Kooskõlastamiseks esitatud eelnõud','http://eelnoud.valitsus.ee/main/mount/rss/home/review.rss' ], \
[u'Valitsusele esitatud eelnõud','http://eelnoud.valitsus.ee/main/mount/rss/home/submission.rss' ] \
# ['bbc','http://feeds.bbci.co.uk/news/rss.xml?edition=int' ] \
]

from utils import *


# We need this because ordinary dictionaries can't have duplicate keys (check the case of delfi.ee)
cat_dict = defaultdict(list)  # TODO! fix issue with dict removing duplicate keys (eg. multiple Postimees sources)
for listitem in categories:
  cat_dict['categories'].append(listitem)

# add custom RSS categories to category list
datastore_results = models.CustomCategory.query(models.CustomCategory.category_type == 'rss_source').fetch()
if datastore_results:
  for result in datastore_results:
    cat_dict['categories'].append([result.category_name,result.category_link])


def parse_results_ilmumas(ilmumas_links,querywords):
    results=[]
    url_base='http://www.riigiteataja.ee/'
    for a in ilmumas_links:
        ourlink=a+'&kuvaKoik=true' # et kuvaks kõik tulemused (riigiteataja lehel pagination)
        src=urllib2.urlopen(ourlink)
        soup = bs4.BeautifulSoup(src.read())
        
        soup = soup.find('tbody')
        
        # down below is a duplicate cycle - could be rafactored
        for q in querywords:
            if ' ' in q: # if space in query, then search for all words
                new_q=set(q.split(' ')) # add to a set
            elif q=='':
                new_q=''
            else:
                new_q=[q]
 
            for result in soup.findAll("tr"):
                cats=[]
                if all([x2.lower() in unicode(result).lower() for x2 in new_q]): # kas märksõnad tulemuses?
                
                  if result.findAll('a'): # kui leiad lingi, tee uus pealkiri ning link (muidu läheb pekki)
                    newlink = url_base+result.a.get('href')
                    newtitle = result.a(text=True)[0]
                  for item in result.findAll("td"): # find columns
                      result2 = item.find_next(text=True)
                      result2 = re.sub('\n', '', result2.rstrip()) # don't know why I need this
                      cats.append(result2) # add results to list
                  
                  # let's parse results
                  if not cats[0]: #
                    item_title=newtitle
                    item_title = item_title.replace("\t", "")
                    item_link=newlink
                  else:
                    item_title=cats[0]
                    item_title = item_title.replace("\t", "")
                    item_link=ourlink
                  """ Have to use some regex to extract dates """
                  if cats[1][0:5]=='RT I,':
                    match = re.search(r'(?<=^.{6}).*', cats[1])
                  elif cats[1][0:7]=='RT III,':
                    match = re.search(r'(?<=^.{8}).*', cats[1])
                  else:
                    match = re.search(r'(?<=^.{7}).*', cats[1])
                  item_date=str(match.group())[0:10]

                  results.append([item_link,item_title,sql_normalize_date(item_date),q,cats[2]])
            
                  # link, title, date, queryword, category

    return results


def parse_feed(querywords, category, date_algus='2016-01-01'):
    date_algus = datetime_object(date_algus)
    results = []
    for cat in cat_dict['categories']:

      if category == cat[0]:  # veendume, et võtame õige allika
        search_from = cat[1]
        logging.error(search_from)

        if category == u'Riigiteataja ilmumas/ilmunud seadused':  # juhul kui tegi riigiteataja ilumas/ilmunud, toimetame teisiti (neil RSS vana ja ei vasta standarditele)
          try:
            src2=urllib2.urlopen(search_from).read(5000) # timeout set (search from, timeout=60) because of default appengine limits (and since riigiteataja ilmumas takes long time to open otherwise too)
            soup2 = bs4.BeautifulSoup(src2)
            if soup2: # kui leiame tulemusi
              limiter=10  # see on vajalik, sest app engine ei saa aru read(5000) limiidist, ning teeb kuni timeout'ini avamist
              links_collection=[]
              while limiter>0:
                for link in soup2.findAll("link"):
                  if len(link.next)>50:
                    links_collection.append(link.next)
                    limiter-=1  # count down until 0 (optimization)
              results.extend(parse_results_ilmumas(links_collection, querywords))
          except Exception, e:
            pass
            logging.error(e)

        else:  # Tegu normaalsete RSSidega
          try:
            if category == 'Finantsministeerium':
              search_from = urllib2.urlopen(search_from, timeout=40)  # without timeout doesn't work
            elif category == u'Kooskõlastamiseks esitatud eelnõud':
              search_from = urllib2.urlopen(search_from, timeout=40).read(20000)

            d = feedparser.parse(search_from)
            for a in d.entries:
              for x in querywords:
                result_title = None
                if ' ' in x:
                  new_x = set(x.split(' '))  # add to a set
                elif x == '':
                  new_x = ''
                else:
                  new_x = [x]

                result_date = datetime.datetime.now().date()
                if category in ['eurlex kohtuasjad','eurlex komisjoni ettepanekud',u'eurlex parlament ja nõukogu']:
                  if result_date >= (date_algus if date_algus else result_date) and (x.lower() in a['title'].lower()):
                    result_title = a['title']
                    result_link = a['link']
                    results.append([result_link, result_title, str(result_date), x, category])

                else:
                  """ Tavaline RSS """
                  try:
                    result_date = dt.fromtimestamp(mktime(a['published_parsed'])).date()
                  except Exception:
                    pass

                  if not result_date:
                    try:
                      result_date = a['published']
                    except Exception:
                      result_date = a['pubDate']
                      pass

                  # Sometimes we get empty blocks, let's catch them and pass

                  summary = a.get('summary')
                  title = a.get('title')
                  description = a.get('description')
                  if summary or title or description:
                    for queryword in new_x:
                      if queryword.lower() in title.lower():
                        result_title = title
                      elif queryword.lower() in description.lower():
                        result_title = description
                      elif queryword.lower() in summary.lower():
                        result_title = summary

                      if result_title:
                        if 'img ' in result_title:
                            break
                        result_title = result_title.replace('<p>','').replace('</p>','')
                        result_link = a['link']
                        results.append([result_link, result_title, str(result_date), x, category])
          except Exception,e:
            logging.error(e)
            pass
    return results  #results if results else None


# TESTING #####
if __name__ == "__main__":
  #results=parse_feed(['president',u'jürgen ligi'],'postimees.ee','2014-01-01')
  #results=parse_feed(['president'],'delfi.ee','2014-01-01')
  #results=parse_feed([''],u'Valitsusele esitatud eelnõud','2015-11-25')
  results=parse_feed([''],'bbc','2015-11-25')
  #results=parse_feed(set([u'teenis']),'Finantsministeerium','2015-01-07')
  #results=parse_feed('redbaltic',set([u'tunnistas']),'17.07.2014')
  #results=parse_feed('lextal',set(['luik']),'01.01.2014') # doesn't work
  #results=parse_feed('eurlex kohtuasjad',['Esimese'],'17.07.2014')
  #results=parse_feed('riigiteataja ilmumas',[u'Keskkonna','seadme'],'17.07.2014')
  print len(results)
  for a in results:
    print a, '\n'