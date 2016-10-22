# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2
import re
from datetime import datetime
import datetime
#from google.appengine.api import search
#import docs
import logging
import urllib

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

from utils import *
 
def search_eurlex(querywords,category,date_algus='01.08.2014'):
    results=[]
    for query in querywords:
      #query=urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      url="http://eur-lex.europa.eu/search.html?instInvStatus=ALL&text=" + query + "&qid=&DTC=false&DTS_DOM=EU_LAW&textScope=ti-te&type=advanced&lang=et&SUBDOM_INIT=EU_LAW_ALL&DTS_SUBDOM=EU_LAW_ALL"
      
      url=" http://eur-lex.europa.eu/search.html?textScope0=ti-te&qid=1431535875346&CASE_LAW_SUMMARY=false&DTS_DOM=ALL&type=advanced&lang=en&andText0=President&SUBDOM_INIT=ALL_ALL&DTS_SUBDOM=ALL_ALL"
      src=urllib2.urlopen(url)
      results.extend(parse_results_eurlex(src,query))
    return results


def parse_results_eurlex(src,query=None): 
    url_base="https://www.riigiteataja.ee"
    soup = bs4.BeautifulSoup(src.read())

    results=[]
    soup = soup.find('tbody')
    try:
      for result in soup.findAll("tr"):
          cats=[]
          linkitem=result.findNext('a', href=True) # leiame lingi
          #logging.error(linkitem)
          cats.append(linkitem.get('href'))
          
          for item in result.findNext('td',attrs={"class": "publicationTitle"}):
              stringitem=str(item.findNext(text=True).next_sibling).decode('utf-8') # unicode type, muidu re ei tööta
              stringitem = re.sub('<br/>', '', stringitem.rstrip())
              stringitem = re.sub('</strong>', '', stringitem.rstrip())
              stringitem = re.sub('<strong>', '', stringitem.rstrip())
              cats.append(stringitem)
              #logging.error(stringitem)
          results.append(cats)
      
      results2=[]
      for doc in results:
        item_date=doc[0]
        item_title=doc[1]
        item_link=url_base+doc[0]
        results2.append([item_link,item_title,sql_normalize_date(item_date),query,u'eurlex']) # check this utf-8
        #logging.error(results2)
      return results2
    except Exception:
      pass
 
# TESTING #####
if __name__ == "__main__":
 # results=search_fi([u'börs','fond'],'FI kehtivad juhendid','2014-12-07') # FI kehitvad juhendid
  results=search_eurlex([u'President'],'Eur-Lex','2015-01-01') # FI kehitvad juhendid
  #results=search_EU_supervision(['solventsus','konsult'],u'EIOPA teated','2014-12-01')

  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close..')
# ########################
