# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2

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




def search_seadused(querywords, category, date_algus='2010-01-01'):
    date_algus = datetime_object(date_algus)
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


from operator import itemgetter
import models
from google.appengine.api import search
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

    search_law_names = []
    paragraph_words =  ['paragraaf','paragrahv',u'§','para']
    search_law_name = None
    search_para_nbr = None

    if any(x in query for x in paragraph_words) or filter(str.isdigit, query.replace(u'§','').encode('latin1')):
      # get paragraph number to limit searches (if we have indication that we're search for a specific paragraph))
      # remove paragraph words from search string
      search_para_nbr = filter(str.isdigit, query.replace(u'§','').encode('latin1'))  # find digit, but replace paragraph symbpl first

    laws_titles = models.RiigiTeatajaMetainfo.query().fetch()
    for law in laws_titles:
      query2 = ''.join([e for e in query.replace(u'§','').split() if e.lower() not in paragraph_words + ['seadus', search_para_nbr]])
      query4 = [e for e in query.replace(u'§','').split() if e.lower() not in paragraph_words + ['seadus', search_para_nbr]][0]
      query3 = query.replace(u'§','').split()[0]
      #logging.error(repr(query4))
      #logging.error(repr(query5))
      logging.error(repr(query))
      logging.error(repr(law.title.lower().replace(' ','')))
      if (query2.lower() in law.title.lower().replace(' ','')
            or query4.lower() in law.title.lower().replace(' ','')
            or query3.lower() in law.title.lower()  # ["lõhkematerjali","seadus","paragrahv"][0]
            or law.title.lower() in query.lower()
            or any(x.lower() in ''.join(law.title).encode('utf8').lower() for x in [e for e in query.replace(u'§','').encode('latin1').split() if e.lower() not in paragraph_words + ['seadus', search_para_nbr]])
          ):
        logging.error(2)
        search_law_names.append(law.title)

    if len(search_law_names) > 0:  # TODO! think what to do when we don't get law name?
      logging.error(repr(search_law_names))
      final_results = []
      for search_law_name in search_law_names:

        try:  # try is only here because "Euroopa Parlamendi ja n├Ąukogu m├ż├żruse (E├£) nr 1082/2006 ┬½Euroopa territoriaalse koost├Č├Č r├╝hmituse (ETKR) kohta┬╗ rakendamise seadus" is exceeds 100byte limit for index name
          index = search.Index(name=search_law_name.encode('ascii', 'ignore').replace(' ',''))  # index name is printable ASCII

          if len(query2.split()) == 1 and search_para_nbr:
            #logging.error(query2.split())
            query_string = 'para_nbr=%s' % search_para_nbr
            results = index.search(query_string)
            for result in results:

              rank = 0
              for single_query in query.split():
                try:
                  # rank results (had to split query only for ranking here)
                  if result.field('para_nbr').value == int(search_para_nbr):
                      rank += 1
                  if single_query.lower() in result.field('law_title').value.lower():
                      rank += 1
                  if single_query.lower() in result.field('content').value.lower():
                      rank += 2
                except Exception:
                  pass

              final_results.append([result.field('law_link').value,
                                      result.field('content').value,
                                      result.field('para_title').value,
                                      result.field('law_title').value,
                                      rank, rank])


          else:
            for single_query in query.split():
              query_string = 'content: ~"%s"' % (single_query)
              results = index.search(query_string)
              if results:
                for result in results:
                  try:
                    # rank results
                    rank = 0
                    if single_query.lower() in result.field('law_title').value.lower():
                        rank += 1
                    if single_query.lower() in result.field('content').value.replace(' ','').lower():
                        #logging.error('adding +2 from content because %s exists in %s' %(single_query.lower(), result.field('content').value.replace(' ','').lower()))
                        rank += 2
                  except Exception:
                    pass
                  final_results.append([result.field('law_link').value,
                                        result.field('content').value,
                                        result.field('para_title').value,
                                        result.field('law_title').value,
                                        rank, rank])

        except Exception, e:
            logging.error(e)
            pass


      print "total results: %d" % len(final_results)
      final_results = sorted(final_results, key=itemgetter(5), reverse=True)
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
 
 

# TESTING #####
if __name__ == "__main__":
  #results=search_kohtu([u'Eldar Plakan','Margus Sepp',u'Vladimir Kolobaškin'],'maa- ja ringkonnakohtu lahendid', '2011-01-01') # site often down
  #results=search_eelnou([''],u'eelnõud','2000-01-01') # 'buss','alkohol'
  results=search_oigusaktid(['buss','alkohol'],u'õigusaktid','2000-01-01')
  
  #results = search_ametlikud_teadaanded([u'sõjaväe'],u'Ametlikud teadaanded','2015-01-01')
  #results=search_riigiteataja_uudised(['Euroopa'],u'riigiteataja kohtuuudised','2011-01-01') 
  #results=search_riigiteataja_uudised(['Euroopa'],u'riigiteataja seadusuudised','2011-01-01') 

  for a in results:
    print a, '\n' , '\n'
# ########################