# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2
import re
from datetime import datetime
import datetime
import logging
import urllib
from collections import defaultdict

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

from utils import *

categories = [\
[u'euroopa pangandusjärelevalve EBA','http://www.fi.ee/index.php?id=13371&year=2014'], \
[u'ühtne pangandusjärelevalve SSM','http://www.fi.ee/index.php?id=16881&year=2014'], \
['EIOPA teated','http://www.fi.ee/index.php?id=13373&year=2015'], \
['EIOPA teated','http://www.fi.ee/index.php?id=13373&year=2014'], \
['ESMA teated','http://www.fi.ee/index.php?id=13375&year=2015'], \
['ESMA teated','http://www.fi.ee/index.php?id=13375&year=2014'], \
['FI pressiteated','http://www.fi.ee/index.php?id=1080&year=2015'], \
['FI pressiteated','http://www.fi.ee/index.php?id=1080&year=2014'], \
]
# We need this because ordinary dictionaries can't have duplicate keys (check the case of delfi.ee)
cat_dict = defaultdict(list)
for listitem in categories:
  cat_dict['categories'].append(listitem)
  
def search_EU_supervision(querywords,category, date_algus='2013-01-01'):
  date_algus=datetime_object(date_algus)
  date_algus_format  = date_algus.strftime("%d.%m.%Y")
  final_results=[]
  #for query in querywords:
  url_base='http://www.fi.ee'
  
  for cat in cat_dict['categories']:
    search_from=cat[1]
    if category==cat[0]:
      src=urllib2.urlopen(search_from,timeout=60)
      soup2 = bs4.BeautifulSoup(src)
      results=[]
      if soup2:
        soup2 = soup2.find('div', attrs={"class": "newslist"})
        for result in soup2.findAll('div', attrs={"class": "item"}):
            #print result
            cats=[]
            linkitem=result.findNext('a', href=True) # leiame lingi
            #print linkitem.get('href')
            cats.append(linkitem.get('href'))

            stringitem=result.findAll(text=True)
            cats.append(stringitem[1:4][0])
            cats.append(stringitem[1:4][2])
            results.append(cats)

        results2=[]
        for doc in results:
          item_date=doc[1]
          item_title=doc[2]
          item_link=url_base+doc[0]
          for query in querywords:
            if query.lower() in item_title.lower(): # Kui leiame otsingusõna
              if datetime_object(sql_normalize_date(item_date))>=date_algus:
                results2.append([item_link,item_title,sql_normalize_date(item_date),query,category,0]) # check this utf-8
            
        final_results.extend(results2)
  return final_results
        
 
def search_fi(querywords,category,date_algus='2013-01-01'):
    date_algus=datetime_object(date_algus)
    date_algus_format  = date_algus.strftime("%d.%m.%Y")
    """ Somehow source is fucked up... need to remove certain characters like smart quotes etc """
    final_results=[]
    #query2=urllib.quote_plus(query.encode('utf-8')) # asendab tühiku +'iga, muudab mitte ascii'd formaati %C5%A1
    # ehitame otsinglingi
    url2="http://www.fi.ee/index.php?id=2898" # Finantsinspektsiooni juhendite projektid
    url3="http://www.fi.ee/index.php?id=2897" #  Finantsinspektsiooni kehtivad juhendid
    
    
    if category=='FI juhendite projektid':
        url=url2
    if category=="FI kehtivad juhendid":
        url=url3
    src=urllib2.urlopen(url)
    #print src.headers['content-type']
    result = parse_results_fi(src,querywords,category,date_algus)
    if result:
      final_results.extend(result)
    
    return final_results


def parse_results_fi(src,querywords=None,category=None,date_algus=None): 
    #url_base="https://www.riigiteataja.ee"
    #soup = bs4.BeautifulSoup(src.read())
    soup = bs4.BeautifulSoup(src.read(), 'html5lib')

    results=[]
    soup = soup.find('div', attrs={"class": "contentbox"})

    for result in soup.findAll("tr"):
      
      #if unicode(query.lower()) in unicode(result).lower():
      cats=[]
      linkitem=result.findNext('a', href=True) # leiame lingi
      cats.append(linkitem.get('href'))
      
      for item in result.findAll('td'): # ,attrs={"class": "publicationTitle"}
        stringitem=item.find_next(text=True) #.decode('utf-8') # unicode type, muidu re ei tööta
        # Replace "smart" and other single-quote like things
        stringitem = re.sub(
            u'[\u02bc\u2018\u2019\u201a\u201b\u2039\u203a\u300c\u300d\xe2\u20ac\u0153]',
            "'", stringitem)
        # Replace "smart" and other double-quote like things
        stringitem = re.sub(
            u'[\u00ab\u00bb\u201c\u201d\u201e\u201f\u300e\u300f]',
            '"', stringitem)
        stringitem = re.sub('<br/>', '', stringitem.rstrip())

        cats.append(stringitem)
      
      results.append(cats)
      
    results2=[]
    if results:
      for result in results:
        if "Juhendi pealkiri" not in result:
          item_date=result[3]
          item_title=result[1]

          item_title=''.join(chr(ord(c)) for c in item_title).decode('utf8',errors='ignore') # needed because src is fked
          item_date=''.join(chr(ord(c)) for c in item_date).decode('utf8',errors='ignore') # needed because src is fked

          item_link=result[0]
          for query in querywords:
            if query.lower() in item_title.lower() or query.lower() in item_link:
              #if datetime_object(sql_normalize_date(item_date))>=date_algus:
              results2.append([item_link,item_title,sql_normalize_date(item_date),query,category,0])
      #print item_title.encode('utf-8')

    return results2
 
# TESTING #####
if __name__ == "__main__":
 # results=search_fi([u'börs','fond'],'FI kehtivad juhendid','2014-12-07') # FI kehitvad juhendid
  results=search_EU_supervision([u'emit'],'ESMA teated','2015-01-01') # FI kehitvad juhendid
  #results=search_EU_supervision(['solventsus','konsult'],u'EIOPA teated','2014-12-01')

  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close..')
# ########################
