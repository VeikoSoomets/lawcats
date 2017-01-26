# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2
import re
from datetime import datetime
import datetime
#from google.appengine.api import search
import logging
import urllib
# lets test change

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(45)

from utils import *

categories = {
        'Hiljutised Riigikohtu lahendid':'http://www.nc.ee/',
        }

def search_kohtu(querywords,category,date_algus='2013-01-01'):
    date_algus=datetime_object(date_algus)
    date_algus_format  = date_algus.strftime("%d.%m.%Y")
    results=[]
    for query in querywords:
      query2=urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      # ehitame otsinglingi
      url="http://www.nc.ee/?id=11&lahendid[kohtuasjad.aasta]=&lahendid[kohtuasjad.kohtuasja_tyyp]=&lahendid[kohtuasjad.regnr]=&lahendid[kohtuasjad.otsuse_kuupaev]=&lahendid[kohtuasja_istungid.koosseisu_tunnus]=&lahendid[kohtuasjad.tyyp]=&lahendid[kohtuasja_marksonad.annotatsioon]=&lahendid[kohtuasjad.tekst]=" + query2 + "&lahendid[s1]=kohtuasjad.otsuse_kuupaev&lahendid[o1]=desc&lahendid[s4]=kohtuasjad.sisu"
      #logging.error(url)
      src=urllib2.urlopen(url)
      result = parse_results_kohtu(src,query,category,date_algus)
      if result:
        results.extend(result)
    return results
      # testimiseks kasuta alumist, siis sa ei koorma riigiteatajat
      
      #with open("riigiteataja_tulemus.txt", 'r') as src:
      #    return parse_results_kohtu(src)
          
    
def parse_results_kohtu(src,query=None,category=None,date_algus=None): 
    url_base="http://www.nc.ee/"
    
    encoding=src.headers['content-type'].split('charset=')[-1] # we have to use this fix or EE letters are causing trouble
    soup = bs4.BeautifulSoup(src, from_encoding=encoding)
    #soup = bs4.BeautifulSoup(src.read())

    results=[]
    soup = soup.find('table')
    try:
      for result in soup.findAll("tr"):
          cats=[]
          linkitem=result.findNext('a', href=True) # leiame lingi
          cats.append(linkitem.get('href'))
          for item in result.findAll("td"):
              stringitem=item.findNext(text=True) # leiame teksti
              cats.append(stringitem)
          results.append(cats)
          #logging.error(results)
      
      results2=[]
      for doc in results[1:]: # esimene tulemus tuleb moondatud (sest esimene <tr> on väljanimed tulemustes)
        #logging.error(doc)
        item_date=doc[1]
        item_title=doc[3]
        item_link=url_base+doc[0]
        if datetime_object(sql_normalize_date(item_date))>=date_algus:
          results2.append([item_link,item_title,sql_normalize_date(item_date),query,category,0])
      
      return results2  
    except Exception:
      pass

#	Aleksandr Puškarjovi
# TESTING #####
if __name__ == "__main__":
  results=search_kohtu([u''],'Riigikohtu lahendid','2013-04-01')  # Aleksandr Puškarjov
  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close...')
# ########################