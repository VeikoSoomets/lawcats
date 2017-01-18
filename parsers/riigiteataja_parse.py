# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2

from datetime import datetime
import datetime
#from google.appengine.api import search
#import docs
import logging
import urllib


from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(45)

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

from utils import *
    
categories_uudised = {
        'Riigiteataja seadusuudised':'otsiSeadusteUudised',
        'Riigiteataja kohtuuudised':'kohtuuudiste_otsingu_tulemused',
        u'Riigiteataja õigusuudised':'otsiMuuOigusuudised'
        }
categories_seadused = {
        'Riigiteataja seadused':''
        }


def search_ametlikud_teadaanded(querywords, category, date_algus='2010-01-01'):
    date_algus = datetime_object(date_algus)
    date_algus_format = date_algus.strftime("%d.%m.%Y")
    results = []
    date_lopp = None
    for query in querywords:
      query2=urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      #url = "https://www.riigiteataja.ee/kohtuteave/maa_ringkonna_kohtulahendid/otsi.html?kohtuasjaLiik=0&detailsemOtsing=false&kohtuasjaNumber=&lahendiKuupaevAlates=" + date_algus_format + "&lahendiKuupaevKuni=&menetlusKuupaevAlates=&menetlusKuupaevKuni=&_koikAsjaLahendid=on&kohtumajaId=0&lahendiLiikiId=0&lahendiSisu=" + query2 + "&otsi="
      url = "https://www.ametlikudteadaanded.ee/avalik/otsing?o__teate_liigid=&otsi_andmeandjat=&o__andmeandjad_id=&o__search_term=" + query2 + "&ehak_otsing=&o__mojupiirkond=&o__avaldamise_kuupaev_alates=" + date_algus_format + "&o__avaldamise_kuupaev_kuni=&do_search=1" + query2
      result = parse_results_teadaanded(url, query, category, date_algus)
      if result:
        results.extend(result)

    return results


def search_seadused(querywords, category, date_algus='2010-01-01'):
    date_algus = datetime_object(date_algus)
    logging.error(querywords)
    results = []
    for query in querywords:
      result = parse_results_seadused(query, category, date_algus)
      if result:
        results.extend(result)

    return results


def search_kohtu(querywords, category, date_algus='2010-01-01'):
    date_algus = datetime_object(date_algus)
    date_algus_format = date_algus.strftime("%d.%m.%Y")
    results = []
    date_lopp = None
    for query in querywords:
      query2=urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      #url = "https://www.riigiteataja.ee/kohtuteave/maa_ringkonna_kohtulahendid/otsi.html?kohtuasjaLiik=0&detailsemOtsing=false&kohtuasjaNumber=&lahendiKuupaevAlates=" + date_algus_format + "&lahendiKuupaevKuni=&menetlusKuupaevAlates=&menetlusKuupaevKuni=&_koikAsjaLahendid=on&kohtumajaId=0&lahendiLiikiId=0&lahendiSisu=" + query2 + "&otsi="
      url = "https://www.riigiteataja.ee/kohtulahendid/otsingutulemus.html?aktiivneTab=KOIK&sort=LahendiKuulutamiseAeg&asc=false&kohtuasjaNumber=&lahendiKpvAlgus=" + date_algus_format + "&lahendiKpvLopp=&menetluseKpvAlgus=&menetluseKpvLopp=&kohus=&kohtunik=&annotatsiooniSisu=&menetluseLiik=&lahendiLiik=&lahendiTekst=" + query2
      result = parse_results_kohtu(url, query, category, date_algus)
      if result:
        results.extend(result)
    
    return results

 
def search_eelnou(querywords, category, date_algus='2015-01-01'):
    date_algus = datetime_object(date_algus)
    date_algus_format = date_algus.strftime("%d.%m.%Y")

    results=[]
    for query in querywords:
      query2=urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      # ehitame otsinglingi
      url="https://www.riigiteataja.ee/eelnoud/otsing.html?pealkiri=" + query2 + "&tekst=&aktiAndja=&eelnouLiik=&eelnouNumber=&menetluseEtapp=&menetluseAlgus=" + date_algus_format + "&menetlusKuni=&leht=0&kuvaKoik=true"
      #logging.error(url)
      
      result = parse_results_eelnou(url, query, category, date_algus)
      if result:
        results.extend(result)
    return results 


def search_oigusaktid(querywords, category, date_algus='2010-01-01'):
    date_algus = datetime_object(date_algus)
    date_algus_format = date_algus.strftime("%d.%m.%Y")
    results = []
    for query in querywords:
      query2 = urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      if category==u'Kehtivate õigusaktide otsing':
        beginning='&pealkiri='
      elif category==u'Kehtivate KOV õigusaktide otsing':
        beginning='kov=true&pealkiri='
      # NB!!!! siia võib juurde lisada, kas otsida tulevikus jõustuvaid, hetkel kehtivaid jne
      url="https://www.riigiteataja.ee/tervikteksti_tulemused.html?" + beginning + query2 + "&tekst=&valjDoli1=&valjDoli2=&valjDoli3=&nrOtsing=tapne&aktiNr=&minAktiNr=&maxAktiNr=&kehtivuseKuupaev=" + date_algus_format
      #logging.error(url)
      #url="https://www.riigiteataja.ee/tervikteksti_tulemused.html?kov=true&pealkiri=alkohol&tekst=&valj1=K%C3%B5ik+KOV-id&valj2=&valj3=&nrOtsing=tapne&aktiNr=&minAktiNr=&maxAktiNr=&kehtivusKuupaev=12.11.2014&kehtivuseAlgusKuupaev=&kehtivuseLoppKuupaev="
      #logging.error(url)

      result = parse_results_oigusaktid(url, query, category, date_algus)
      if result:
        results.extend(result)

    return results

 
def search_riigiteataja_uudised(querywords,category,date_algus='2010-01-01'):
    date_algus=datetime_object(date_algus)
    date_algus_format  = date_algus.strftime("%d.%m.%Y")
    results=[]
    if category in categories_uudised:
      #logging.error(category)
      for a,b in categories_uudised.iteritems(): # võtame dictionary'st väärtused
        if a==category:
          for query in querywords:
            query = re.sub(' ', '+', query.rstrip()) # asenda tühik +'iga
            
            # vastavalt uudise kategooriale (category tuleb algselt index.html failist) ehitame otsinglingi
            url="https://www.riigiteataja.ee/oigusuudised/" + b + ".html?pealkiri=" + query + "&alates=" + date_algus_format + "&kuni=&kuvaKoik=true"
            #logging.error(url)
            #print url
            
            result= parse_riigiteataja_uudised(url, query, category, date_algus)
            if result:
              results.extend(result)

    return results

import models
import time
from operator import itemgetter
def parse_results_seadused(query=None, category=None, date_algus=None):

    """hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
     'Accept-Encoding': 'none',
     'Accept-Language': 'en-US,en;q=0.8',
     'Connection': 'keep-alive'} """
    """print "fetching start"
    start_time = time.time()
    laws = models.RiigiTeatajaURLs.query().fetch()
    print "fetching took %s seconds" % str(time.time() - start_time) """

    laws = models.RiigiTeatajaURLs.query().fetch()
    itr = 0
    final_results = []
    for law in laws:
      #  limit results by 5
      """itr += 1
      if itr > 5:
        print "iteration limit 5, breaking loop here... "
        break"""

      #req = urllib2.Request(law.link)  # , headers=hdr
      src = law.text

      soup = bs4.BeautifulSoup(src, "html5lib")

      url_base = law.link

      # Get individual articles
      articles = soup.find_all('div', attrs={'id': 'article-content'})
      article_cnt = 0
      for article in articles:
        article_link, title, content = None, None, None
        title = law.title
        # Get content
        content = article.find_all('p')  #, attrs={'class': 'announcement-body'}
        for c in content:
          article_cnt += 1
          try:
            article_link = c.find_next('a').get('name')
            article_link = url_base + '#' + article_link
          except:
            pass

          #content2 = [x.get_text() for x in c]
          # TODO! datelimit -> datetime_object(sql_normalize_date(item_date))>=date_algus
          rank = 0
          for single_word in query.split():
            if single_word.lower() in ''.join(c.get_text().lower()):
              rank += 1

              if single_word.lower() in c.get_text():
                rank += 1

              if single_word.lower() in law.title.lower():
                rank += 1

              #print rank
              content = c.get_text()
              final_results.append([article_link, content, None, title, rank, rank])
    print len(final_results)
    final_results = sorted(final_results, key=itemgetter(5))
    return final_results


def parse_results_teadaanded(link, query=None, category=None, date_algus=None):
    url_base="https://www.ametlikudteadaanded.ee"
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
     'Accept-Encoding': 'none',
     'Accept-Language': 'en-US,en;q=0.8',
     'Connection': 'keep-alive'}
    req = urllib2.Request(link, headers=hdr)  # , headers=hdr
    src = urllib2.urlopen(req)
    encoding = src.headers['content-type'].split('charset=')[-1]  # we have to use this fix or EE letters are causing trouble
    soup = bs4.BeautifulSoup(src.read(), "html5lib", from_encoding=encoding)

    # Get individual articles
    articles = soup.find_all('div', attrs={'class': 'result'})

    final_results = []
    for article in articles:
      article_link, title, content = None, None, None
      try:
        title_tags = ['h2', 'h1', 'h3', 'h4', 'h5']
        for tag in title_tags:
          try:
            title = article.find(tag).find('a')
            article_link = title.get('href')
            title = title.stripped_strings.next()
            if not article_link.startswith('http:', 0, 5):
              article_link = url_base + article_link
          except Exception, e:
            logging.error(e)
            pass
          if title:
            break

        # Get content
        content = soup.find_all('div', attrs={'class': 'announcement-body'})
        content = [x.get_text() for x in content]
        # TODO! datelimit -> datetime_object(sql_normalize_date(item_date))>=date_algus
        if query in ''.join(content):
          final_results.append([article_link, title, None, query, category, 0])

      except Exception, e:
        print e
        continue

      return final_results


def parse_riigiteataja_uudised(url, query=None, category=None, date_algus=None):
    #url_base="https://www.riigiteataja.ee/oigusuudised/"
    #src=urllib2.urlopen(url)
    src = urlfetch.fetch(url, method=urlfetch.GET)
    soup = bs4.BeautifulSoup(src.content)

    results = []
    soup = soup.find('tbody')
    try:
      for result in soup.findAll("tr"):
          cats=[]
          linkitem=result.findNext('a', href=True) # leiame lingi
          #logging.error(linkitem)
          cats.append(linkitem.get('href'))
          #logging.error(bb)
          for item in result.findAll("td"):
              stringitem=item.findNext(text=True) # leiame teksti
              stringitem = re.sub('\r', '', stringitem.rstrip())
              stringitem = re.sub('\t', '', stringitem.rstrip())
              stringitem = re.sub('\n', '', stringitem.rstrip())
              #stringitem = stringitem.decode("utf-8")
              cats.append(stringitem)
          cats.append(linkitem.getText()) # kohtuuudiste jaoks
          results.append(cats)
      
      for a in results:
          if len(str(a))<1:
              results.remove(a)
   
      results2=[]
      url_base="https://www.riigiteataja.ee/oigusuudised/"
      for doc in results:
          #print doc
          #logging.error(str(doc))
          #logging.error(term)
          if category == 'Riigiteataja kohtuuudised': # kohtuuudised
            #logging.error(results)
            item_date = doc[4]
            item_title = doc[5]
          elif category == u'Riigiteataja õigusuudised': # muud õigusuudised
            item_date = doc[2]
            item_title = doc[3]
          elif category == 'Riigiteataja seadusuudised': # seadusuudised
            item_date = doc[2]
            item_title = doc[1]
          
          item_link = url_base+doc[0]
          #print doc[0]
          if datetime_object(sql_normalize_date(item_date))>=date_algus and "facebook" not in str(doc):
            results2.append([item_link, item_title, sql_normalize_date(item_date), query, category, 0])
      return results2
    
    except Exception:
      pass
   # logging.error(results2)


def parse_results_kohtu(url, query=None, category=None, date_algus=None):
    url_base="https://www.riigiteataja.ee"
    # src = urllib2.urlopen(url, timeout=30)

    src = urlfetch.fetch(url, method=urlfetch.GET)
    soup = bs4.BeautifulSoup(src.content)
    results = []
    soup = soup.find('tbody')
    try:
      for result in soup.findAll("tr"):
          cats = []
          linkitem = result.findNext('a', href=True) # leiame lingi
          cats.append(linkitem.get('href'))
          for item in result.findAll("td"):
              stringitem = item.findNext(text=True) # leiame teksti
              cats.append(stringitem)
          results.append(cats)
      
      results2 = []
      for doc in results:
        item_date = doc[6]
        item_title = doc[1]
        item_link = url_base + doc[0]
        
        if datetime_object(sql_normalize_date(item_date)) >= date_algus:
          results2.append([item_link, item_title, sql_normalize_date(item_date), query, category, 0])
      
      return results2
    except Exception:
      pass


def parse_results_eelnou(url,query=None,category=None,date_algus=None):
    url_base="https://www.riigiteataja.ee"
    # src = urllib2.urlopen(url, timeout=10)
    src = urlfetch.fetch(url, method=urlfetch.GET)
    soup = bs4.BeautifulSoup(src.content)

    results = []
    soup = soup.find('tbody')
    try:
      for result in soup.findAll("tr"):
          cats=[]
          linkitem=result.findNext('a', href=True) # leiame lingi
          cats.append(linkitem.get('href'))
          for item in result.findAll("td"):
              stringitem=item.findNext(text=True) # leiame teksti
              cats.append(stringitem)
          results.append(cats)
      
      results2=[]
      for doc in results:
        item_date=doc[4][0:10]  # tee kuupäevaks
        item_title=doc[2]
        item_link=url_base+doc[0]
        
        #print 'date_algus: ' + str(date_algus)
        #print str(datetime_object(sql_normalize_date(item_date)))
        if datetime_object(sql_normalize_date(item_date))>=date_algus:
          results2.append([item_link,item_title,sql_normalize_date(item_date),query,category,0]) # check this utf-8
        #logging.error(results2)
      return results2
    except Exception:
      pass


def parse_results_oigusaktid(url, query=None, category=None, date_algus=None):
    url_base="https://www.riigiteataja.ee"
    # src = urllib2.urlopen(url)
    src = urlfetch.fetch(url, method=urlfetch.GET)
    soup = bs4.BeautifulSoup(src.content)

    results = []
    soup = soup.find('tbody')
    try:
      for result in soup.findAll("tr"):
          cats = []
          linkitem = result.findNext('a', href=True) # leiame lingi
          cats.append(linkitem.get('href'))
          for item in result.findAll("td"):
              stringitem = item.findNext(text=True) # leiame teksti
              cats.append(stringitem)
          results.append(cats)
      
      results2=[]
      for doc in results:
        item_date = doc[5][0:10]
        item_title = doc[1]
        item_link = url_base + doc[0]
        
        if datetime_object(sql_normalize_date(item_date)) >= date_algus:
          results2.append([item_link,item_title,sql_normalize_date(item_date),query,category,0]) # check this utf-8
        #logging.error(results2)
      return results2
    except Exception:
      pass
 
 
def parse_seadus(src,seadus): # pole kasutusel
    #src = '"{0}"'.format(src.replace('"',''))

    """
    with open("KarS.html") as myfile:
        url_base="https://www.riigiteataja.ee/akt/126022014005" #"http://www.ilukabinet.ee/AdvS.html"
    #f = urllib2.urlopen(url_base)
        sisu = myfile.read(1000000) # f.read
    soup = bs4.BeautifulSoup(sisu)

    paraTitles = []
    paraLinks = []
    ptkTitle = []

    for peatykk in soup.findAll("a", {"class": "toggle truncate-toc"}):
        ptk_title = peatykk.findAll(text=True, limit=100)
        ptkTitle.append(ptk_title)
        
    for para in soup.findAll("a", {"class": "truncate2-toc"}):
        paratitle = para.get_text() #para.findAll(text=True, limit=100)
        paralink = para['href'] #"{0}{1}".format(url_base, para['href'])
        paraTitles.append(paratitle)
        paraLinks.append(paralink)
        
    a=soup.find("div", {"id": "article-content"})
    
    delete_all_in_index("KarS") # teeme indeksi tühjaks
    for b, a, l in zip([x for x in a.findAll("p")],paraTitles,paraLinks):
    
        #uus=[x for x in b[4:7] if is_number(x)]
        #print "para" + ''.join(uus)
        #if b.findAll("a", {"name": "truncate2-toc"}
        b = b.get_text() 
        my_document = search.Document(
        # Setting the doc_id is optional. If omitted, the search service will create an identifier.
        #doc_id = 'PA6-5000',
        fields=[
           search.TextField(name='name', value='Karistusseadustik'),
           search.HtmlField(name='paragraph', value=str(a)), #paraTitles
           search.HtmlField(name='content', value=str(b)), # a.findAll("p")
           search.TextField(name='link', value=str(l)), # paraLinks
           search.DateField(name='updated', value=datetime.datetime.now())
           ])
        index = search.Index(name="KarS")
        index.put(my_document) # paneme dokumendi indeksisse
    """
    # Query Index
    #seadus="KarS" # muuta seadust
    index = search.Index(name=seadus) # "AdvS"
    
    # Query String
    query_string = src 

    # Query Options
    query_options = search.QueryOptions(
        limit=20, # something wrong with this
        returned_fields=['content','name','paragraph','link'])#,
        # #snippeted_fields=[docs.Product.CONTENT])
    
    query = search.Query(query_string=query_string, options=query_options)

    rel2=[]
    try:
        results = index.search(query)
            
        """for scored_document in results.results:
            rel2.append(scored_document)  """

    except search.Error:
        logging.exception('Search failed')
    
    return results.results # (paraLinks,paraTitles,rel2)
    
# TESTING #####
if __name__ == "__main__":
  #results=search_kohtu([u'Eldar Plakan','Margus Sepp',u'Vladimir Kolobaškin'],'maa- ja ringkonnakohtu lahendid', '2011-01-01') # site often down
  #results=search_eelnou([''],u'eelnõud','2000-01-01') # 'buss','alkohol'
  #results=search_oigusaktid(['buss','alkohol'],u'õigusaktid','2000-01-01')
  
  results = search_ametlikud_teadaanded([u'sõjaväe'],u'Ametlikud teadaanded','2015-01-01')
  #results=search_riigiteataja_uudised(['Euroopa'],u'riigiteataja kohtuuudised','2011-01-01') 
  #results=search_riigiteataja_uudised(['Euroopa'],u'riigiteataja seadusuudised','2011-01-01') 

  for a in results:
    print a, '\n' , '\n'
# ########################