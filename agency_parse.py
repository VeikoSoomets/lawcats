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

#NB! Fix finding õ,ä,ö.ü
#NB! välisministeerium gets description not title - check others too

pages={
      'haridusministeerium' : 'https://www.hm.ee/et/valitsemisala-uudised', # ssl certificate - not allowed
      'haridusministeerium' : 'https://www.hm.ee/et/uudised', # ssl certificate - not allowed for robot access
      'justiitsministeerium' : 'http://www.just.ee/et/uudised',
      'keskkonnaministeerium' : 'http://www.envir.ee/et/uudised',
      'kultuuriministeerium' : 'http://www.kul.ee/et/uudised',
      'majandusministeerium' : 'https://www.mkm.ee/et/uudised', # ssl certificate - not allowed for robot access
      u'põllumajandusministeerium' : 'http://www.agri.ee/et/uudised',
      'siseministeerium' : 'https://www.siseministeerium.ee/et/uudised',
      'sotsiaalministeerium' : 'http://www.sm.ee/et/uudised',
      u'välisministeerium' : 'http://vm.ee/et/uudised'
  }

def sql_normalize_date(date):
    """ Make dates ready for inserting into SQL. Add new formats if needed. """
    EE_dates = {
    'jaanuar' : '01',
    'jaan' : '01',
    'veebruar' : '02',
    'veeb' : '02',
    'veebr' : '02',
    u'märts' : '03',
    'aprill' : '04',
    'aprill' : '04',
    'mai' : '05',
    'juuni' : '06',
    'juuli' : '07',
    'august' : '08',
    'aug' : '08',
    'september' : '09',
    'sept' : '09',
    'oktoober' : '10',
    'okt' : '10',
    'november' : '11',
    'nov' : '11',
    'detsember' : '12',
    'dets' : '12'
    }     
    
    """ Dates from string, EE """
    for key, month in EE_dates.iteritems():
      if key in date:
        try: # have to use this, because substring will not be found error will be thrown there are no dots in date
          if date.index('.')==1: # in case day is without preceding zero
            day='0' + date[0]
          else:
            day=date[0:2]
        except Exception:
          day=date[0:2]
        date=day + '.' + month + '.' + date[-4:]
    
    try: 
        if date.index('.')==4:
          date=str(datetime.datetime.strptime(date, '%Y.%m.%d').date())
        else:
          date=str(datetime.datetime.strptime(date, '%d.%m.%Y').date())
    except ValueError:
        date=date
        
    
    return date
    
def search_ministry(querywords,date_algus,allikas):
  final_results=[]
  for query in querywords:

    for key,search_from in pages.iteritems():
      baseurl=search_from
      if allikas==key:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          soup2 = soup2.find('div', attrs={"class": "view-content"})
          for result in soup2.findAll('div', attrs={'class' : 'views-row'}):
              #print result
              cats=[]
              linkitem=result.findNext('a', href=True) # leiame lingi
              #print linkitem.get('href')
              cats.append(linkitem.get('href'))
              stringitem=result.findAll(text=True)
              cats.append(stringitem) # date
              results.append(cats)

          results2=[]
          for doc in results:
            item=doc[1]

            #print item[8]
            
            item_date=item[3]
            item_title=item[9]
            
            if len(item_title)<4: # for some reason sotsiaalministeerium needs this)
              item_title=item[8]
            if len(item_date)<4:
              item_date=item[4] 
              
            item_link=baseurl + doc[0]

            if query.lower() in str(item).lower(): # Kui leiame otsingusõna
              results2.append([item_link,item_title,sql_normalize_date(item_date),query,allikas]) # check this utf-8
              
          final_results.extend(results2)
  return final_results

  
# TESTING #####
if __name__ == "__main__":
  #results=search_ministry([u'miljard', u'roll'],'01.01.2000','justiitsministeerium') # 
  #results=search_ministry([u'lendleb'],'01.01.2000','keskkonnaministeerium') # 
  #results=search_ministry([u'arengukava'],'01.01.2000','kultuuriministeerium') # 
  #results=search_ministry([u'suve'],'01.01.2000','majandusministeerium') # 
  #results=search_ministry([u'100'],'01.01.2000',u'põllumajandusministeerium') # 
  #results=search_ministry([u'politsei'],'01.01.2000',u'siseministeerium') # 
  #results=search_ministry([u'miljon'],'01.01.2000',u'sotsiaalministeerium') # 
  results=search_ministry([u'ameerika'],'01.01.2000',u'välisministeerium') # 
  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close..')
# ########################
