# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
import bs4
import urllib2 # needed?
from google.appengine.api import urlfetch
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
#['Haridusministeerium','https://www.hm.ee/et/valitsemisala-uudised'], # SSL fail \
#['Haridusministeerium','https://www.hm.ee/et/uudised'], # SSL fail \
['Justiitsministeerium','http://www.just.ee/et/uudised'], \
['Keskkonnaministeerium','http://www.envir.ee/et/uudised'], \
['Kultuuriministeerium','http://www.kul.ee/et/uudised'], \
#['Majandusministeerium','https://www.mkm.ee/et/uudised'], # SSL fail \ 
[u'Põllumajandusministeerium','http://www.agri.ee/et/uudised'], \
['Siseministeerium','https://www.siseministeerium.ee/et/uudised'], \
['Sotsiaalministeerium','http://www.sm.ee/et/uudised'], \
[u'Välisministeerium','http://vm.ee/et/uudised'], \
]

# We need this because ordinary dictionaries can't have duplicate keys (check the case of delfi.ee)
cat_dict = defaultdict(list)
for listitem in categories:
  cat_dict['categories'].append(listitem)


def search_ministry(querywords, category, date_algus):
  if not date_algus:
    date_algus = "2013-01-01"
  date_algus=datetime_object(date_algus)
  #date_algus_format  = date_algus.strftime("%d.%m.%Y")
  final_results=[]
  
  for cat in cat_dict['categories']:
    search_from=cat[1]
    baseurl=search_from
    if category==cat[0]:
      src=urlfetch.fetch(search_from,validate_certificate=False)  # validate certificate bypass doesn't work
      #src=urllib2.urlopen(search_from,timeout=60)
      
      encoding=src.headers['content-type'].split('charset=')[-1] # we have to use this fix or EE letters are causing trouble
      soup2 = bs4.BeautifulSoup(src.content, from_encoding=encoding)
      results=[]
      if soup2:
        #soup2=soup2.prettify('latin1', formatter='html')
        soup2 = soup2.find('div', attrs={"class": "view-content"})
        try:
          for result in soup2.findAll('div', attrs={'class' : 'views-row'}):
              cats=[]
              linkitem=result.findNext('a', href=True) # leiame lingi
              cats.append(linkitem.get('href'))
              stringitem=result.findAll(text=True)
              #stringitem=stringitem.prettify('latin1', formatter='html')
              cats.append(stringitem) # date
              results.append(cats)

          results2=[]

          for doc in results:
            item=doc[1]
            item_date=item[3]
            item_content=item[9]
            item_title=item[7]

            if len(item_title)<4: # for some reason some ministry pages structure is a bit different
              item_title=item[8]
              item_content=item[10]
              
            if len(item_date)<4:
              item_date=item[4] 
              
            #item_content = unicode(item_content)
            item_link=baseurl + doc[0]
                   
            for query in querywords:
              #if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content).lower():
              print 
              if query.lower() in unicode(item_content).lower() or query.lower() in unicode(item_title).lower() : # Kui leiame otsingusõna
                if datetime_object(sql_normalize_date(item_date))>=date_algus:
                  #print repr(item_title)
                  #print repr(item_title.encode('latin1'))
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category,0]) # check this utf-8
              
          final_results.extend(results2)
        except Exception, e:
          print e
          pass
  return final_results

  
# TESTING #####
if __name__ == "__main__":

  #results=search_ministry([u'arengukava'],'Kultuuriministeerium','2010-01-01') # 
  #results=search_ministry([u''],u'Põllumajandusministeerium','2012-01-01') #  
  #results=search_ministry([u'töövisiit',u'ameerika','suursaadik'],u'Välisministeerium','2013-04-01') # 
  #results=search_ministry([u'ü'],u'Siseministeerium','2012-01-01') # 
  results=search_ministry(['roll'],'Justiitsministeerium','2010-01-01')
  #results=search_ministry([''],'Siseministeerium','2010-01-01')
  #results=search_ministry([u'miljon'],u'Sotsiaalministeerium','2012-01-01') #  TEST
  #results=search_ministry(['nutikaid','VKG'],'Keskkonnaministeerium','2010-01-01') # TEST
  
  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close..')
# ########################
