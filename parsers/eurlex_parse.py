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
      encoded_query = urllib.quote_plus(query.encode('utf-8'))  # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
      url = "http://eur-lex.europa.eu/search.html?textScope0=ti-te&qid=1485454656290&CASE_LAW_SUMMARY=false&DTS_DOM=ALL&type=advanced&lang=et&andText0=" + encoded_query + "&SUBDOM_INIT=ALL_ALL&DTS_SUBDOM=ALL_ALL&locale=et"
      src = urllib2.urlopen(url)
      results.extend(parse_results_eurlex(src, query, category))
    return results


def parse_results_eurlex(src, query=None, category=None):  # TODO! get more than 10 results
    soup = bs4.BeautifulSoup(src.read())
    results=[]
    soup = soup.find('tbody')
    try:
      for result in soup.findAll('td', attrs={"class": "publicationTitle"}):
          baseitem = result.findNext('a', href=True)

          stringitem = ''.join(baseitem(text=True))
          linkitem = baseitem.get('name')
          results.append([linkitem, stringitem, None, query, category])

    except Exception ,e:
      print e
      pass

    return results


# TESTING #####
if __name__ == "__main__":
 # results=search_fi([u'börs','fond'],'FI kehtivad juhendid','2014-12-07') # FI kehitvad juhendid
  results = search_eurlex([u'hispaania euroopa fond'],'Eur-Lex','2015-01-01') # FI kehitvad juhendid
  #results=search_EU_supervision(['solventsus','konsult'],u'EIOPA teated','2014-12-01')

  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close..')
# ########################
