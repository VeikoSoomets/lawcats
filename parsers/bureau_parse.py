# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs') # if you don't have this, bs4 will not work

import os
file_dir = os.path.dirname(os.path.abspath(__file__))
new_path = os.path.split(file_dir)[0]
sys.path.insert(0, new_path) # to get utils from root folder.. this might be obsolete

import bs4
import urllib2
import re
import datetime
import logging
import urllib
from collections import defaultdict
#import datetime_object
from utils import * #datetime_object

""" NB! Sources here won't give error when not encapsulated in try except """

categories = [\
['Aivar Pilv','http://apilv.ee/uudised/'], \
['Alterna','http://alternalaw.ee/est/firmast#uudised'], \
['Borenius','http://borenius.ee/uudised/'], \
['Concordia','http://www.concordia.ee/uudised/'], \
['Glimstedt','http://www.glimstedt.ee/publikatsioonid/1045'], \
['Tark Grunte Sutkiene','http://www.tarkgruntesutkiene.com/uudised/kasulik/'], \
['Tark Grunte Sutkiene','http://www.tarkgruntesutkiene.com/uudised/bueroo-uudised/'], \
['Tark Grunte Sutkiene','http://www.tarkgruntesutkiene.com/uudised/tehingud-ja-tunnustus/'], \
['Varul publikatsioonid','http://www.varul.com/publikatsioonid/'], \
['Baltic Legal Solutions','http://www.concordia.ee/uudised/'], \
#['Raidla, Lejins & Norcou','http://www.rln.ee/est/uudised/'], # BROKEN \
#['Raidla, Lejins & Norcou','http://www.rln.ee/est/uudisteleht/'], # BROKEN \
]
#'lextal' : 'http://www.lextal.ee' # doesn't work, has robots.txt
#'Sorainen' : 'http://www.sorainen.com/et/RSS/language/et/content_module/All', # olemas RSS parse failis

# We need this because ordinary dictionaries can't have duplicate keys (check the case of delfi.ee)
cat_dict = defaultdict(list)
for listitem in categories:
  cat_dict['categories'].append(listitem)
  
class LawfirmParsers():
  
  @classmethod
  def search_alterna(self,querywords,category,date_algus='2012-01-01'): 
    date_algus=datetime_object(date_algus)
    final_results=[]
    urlbase = 'http://www.alternalaw.ee'

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          soup2 = soup2.find('section', attrs={"id": "uudised"})
          try:
            for result in soup2.findAll('li', attrs={'class':'news-content'}):
                #print result
                cats=[]
                linkitem=result.findNext('a', href=True) # leiame lingi
                link = urlbase + linkitem.get('href')
                #print linkitem.get('href')
                cats.append(link)
                stringitem=result.findAll(text=True)
                cats.append(stringitem) # date
                results.append(cats)

            results2=[]
            for doc in results:
              item=doc[1]
              item_link=doc[0]
              item_title=item[2]
              item_content=item[8]
              #print repr(item_content)
              item_date=item[5]
              for query in querywords:
                if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                  if datetime_object(sql_normalize_date(item_date))>=date_algus:
                    results2.append([item_link,item_title,sql_normalize_date(item_date),query,category])
            final_results.extend(results2)
          
          except Exception:
            pass
          
    return final_results
  
  @classmethod
  def search_bls(self,querywords,category,date_algus='2012-01-01'): 
    date_algus=datetime_object(date_algus)
    final_results=[]

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          #soup2 = soup2.find('content')
          for result in soup2.findAll('div', attrs={'class' : 'news_latest_news'}):
              #print result
              cats=[]
              linkitem=result.findNext('a', href=True) # leiame lingi
              link = linkitem.get('href')
              #print linkitem.get('href')
              cats.append(link)
              stringitem=result.findAll(text=True)
              cats.append(stringitem) # date
              results.append(cats)

          results2=[]
          for doc in results:
            item=doc[1]
            
            item_link=doc[0]
            item_title=item[0]
            item_content=item[2]
            #print repr(item_content)
            item_date=item[1]
            for query in querywords:
              if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                if datetime_object(sql_normalize_date(item_date))>=date_algus:
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category])
              
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_glimstedt(self,querywords,category,date_algus='2011-01-01'): 
    date_algus=datetime_object(date_algus)
    final_results=[]

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          #soup2 = soup2.find('content')
          for result in soup2.findAll('div', attrs={'class' : 'events_item'}):
              #print result
              cats=[]
              linkitem=result.findNext('a', href=True) # leiame lingi
              link = linkitem.get('href')
              #print linkitem.get('href')
              cats.append(link)
              stringitem=result.findAll(text=True)
              cats.append(stringitem) # date
              results.append(cats)

          results2=[]
          for doc in results:
            item=doc[1]
            
            #print item[2]
            
            item_link=doc[0]
            item_title=item[2]
            item_title =  re.sub('\n', '', item_title.rstrip())
            item_date=item[5]
            item_date =  re.sub('\n', '', item_date.rstrip())
            item_date =  re.sub('\t', '', item_date.rstrip())
            item_content = item[7]
            #print repr(item_content)
            #print item_date
            for query in querywords:
              if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                #print sql_normalize_date(item_date)
                if datetime_object(sql_normalize_date(item_date))>=date_algus:
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category])
              
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_lextal(self,querywords,category,date_algus='2012-01-01'):
    date_algus=datetime_object(date_algus)
    final_results=[]

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          soup2 = soup2.find('div', attrs={'class' : 'frontpage-news'})
          for result in soup2.findAll('p'):
              #print result
              cats=[]
              linkitem=result.findNext('a', href=True) # leiame lingi
              link = linkitem.get('href')
              #print linkitem.get('href')
              cats.append(link)
              stringitem=result.findAll(text=True)
              cats.append(stringitem) # date
              results.append(cats)

          results2=[]
          for doc in results:
            item=doc[1]
            
            #print item[2]
            
            item_link=doc[0]
            item_title=item[2]
            item_title =  re.sub('\n', '', item_title.rstrip())
            item_date=item[5]
            item_date =  re.sub('\n', '', item_date.rstrip())
            item_date =  re.sub('\t', '', item_date.rstrip())
            item_content = item[2] # this is not content, but title.. since you don't get access to this site with a robot anyway, let it be
            #print repr(item_content)
            
            for query in querywords:
              if query.lower() in str(item).lower():
                if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category])
          
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_concordia(self,querywords,category,date_algus='2012-01-01'):
    date_algus=datetime_object(date_algus)
    final_results=[]

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          #soup2 = soup2.find('content')
          for result in soup2.findAll('article'):
              #print result
              cats=[]
              linkitem=result.findNext('a', href=True) # leiame lingi
              link = linkitem.get('href')
              #print linkitem.get('href')
              cats.append(link)
              stringitem=result.findAll(text=True)
              cats.append(stringitem) # date
              results.append(cats)

          results2=[]
          for doc in results:
            item=doc[1]
            #print item[7]
            
            item_link=doc[0]
            item_title=item[5]
            item_date=item[7]
            item_content=item[9]
            #print repr(item_content)
            for query in querywords:
              if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                if datetime_object(sql_normalize_date(item_date))>=date_algus:
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category])
          
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_bureau(self,querywords,category,date_algus='2012-01-01'): # osadel büroodel täpselt sama kood (tõenäoliselt sama webmaster)
    date_algus=datetime_object(date_algus)
    final_results=[]

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          soup2 = soup2.find('div', attrs={"id": "content"})
          for result in soup2.findAll():
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
            
            if len(item)>8: # some messy checkup (that we do get a post, not navigational div or whatever)
            
              #print item[9]
              item_date= item[3] # aivar pilv
              if category=='borenius':
                item_date= item[9] # borenius
                
              item_date =  re.sub('\n', '', item_date.rstrip())
              item_date =  re.sub('\t', '', item_date.rstrip())
              item_title=item[1]
              item_content = item[8]
              item_link=doc[0]
              
              for query in querywords:
                if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                #if query.lower() in str(item).lower(): # Kui leiame otsingusõna
                  if datetime_object(sql_normalize_date(item_date))>=date_algus:
                    results2.append([item_link,item_title,sql_normalize_date(item_date),query,category]) # check this utf-8
          
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_tark(self,querywords,category,date_algus='2012-01-01'):
    date_algus=datetime_object(date_algus)
    final_results=[]

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          soup2 = soup2.find('div', attrs={"class": "news-list"})
          for result in soup2.findAll('div', attrs={'class' : 'news-list-item'}):
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
            #print len(item)
            if len(item)>10:
              item_date=item[2][0:2] + '.' + item[4][0:2] + '.20' + item[4][-2:]
              item_content=item[10]
            else:
              item_date='2014-12-31' # random past date, because only recent posting have dates in this site
              item_content=item[4]
              
            item_title=item[8]
            
            #print repr(item_content)
            item_link=doc[0]
            for query in querywords:
              if query.lower() in unicode(item_title).lower() or query.lower() in unicode(item_content):
                if datetime_object(sql_normalize_date(item_date))>=date_algus:
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category]) # check this utf-8
              
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_varul_pub(self,querywords,category,date_algus='2012-01-01'): 
    date_algus=datetime_object(date_algus)
    final_results=[]
    urlbase= 'http://www.varul.com/publikatsioonid'
      
    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          for result in soup2.findAll('tr'):
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
            
            #print item[3]
            item_date=item[3]
            if item_date!='Aasta':
              if len(item_date)==4:
                item_date = '31.12.' + item_date
              item_title=item[1]
              item_link=doc[0]
              for query in querywords:
                if query.lower() in unicode(item_title).lower():
                  if datetime_object(sql_normalize_date(item_date))>=date_algus:
                    results2.append([item_link,item_title,sql_normalize_date(item_date),query,category]) # check this utf-8
              
          final_results.extend(results2)
    return final_results
  
  @classmethod
  def search_raidla(self,querywords,category,date_algus='2012-01-01'): 
    date_algus=datetime_object(date_algus)
    final_results=[]
    urlbase='http://www.rln.ee'

    for cat in cat_dict['categories']:
      search_from=cat[1]
      if category==cat[0]:
        src=urllib2.urlopen(search_from,timeout=60)
        #print src.headers['content-type']
        soup2 = bs4.BeautifulSoup(src)
        results=[]
        if soup2:
          soup2 = soup2.find('table', attrs={"class": "news"})
          for result in soup2.findAll('tr'):
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
            #print item[3]
            item_date = item[1]
            item_date =  re.sub('\n', '', item_date.rstrip())
            item_date =  re.sub('\t', '', item_date.rstrip())
            item_date = '28.' + item_date[0:2] + '.' + item_date[-4:]
            
            item_title=item[3]

            item_link=urlbase + doc[0]
            for query in querywords:
              if query.lower() in unicode(item_title).lower():
                #print repr(item_title)
                if datetime_object(sql_normalize_date(item_date))>=date_algus:
                  results2.append([item_link,item_title,sql_normalize_date(item_date),query,category]) # check this utf-8
              
          final_results.extend(results2)
    return final_results

  
# TESTING #####
if __name__ == "__main__":
  #results=search_bureau([u'koostöö'],'Aivar Pilv','2010-01-01') # aivar pilv
  #results=search_concordia([u'Erika'],'Concordia','2012-01-01') # 
  #results=search_tark([u'balti'],'Tark Grunte Sutkiene','2012-01-01') # 
  #results=search_varul_pub([u'kinnisvara'],'Varul publikatsioonid','2014-01-01') # 
  #results=search_bureau([u'majandus','praktika'],'Borenius','2012-02-02') # borenius
  results=LawfirmParsers.search_raidla([u'ü'],'Raidla, Lejins & Norcou', '2012-01-01') # 
  #results=search_lextal([u'olavi'],'Lextal','2012-01-01') # doesn't work, has robots.txt
  #results=search_glimstedt([u'hange'],'Glimstedt','2011-01-01') # 
  #results=search_bls([u'kinnisvara','paha'],'Baltic Legal Solutions','2012-01-01') # 
  #results=search_alterna([u'artikkel','jagad',u'põlv'],'Alterna','2012-01-01') # alterna
  
  for a in results:
    print a, '\n' , '\n' 
  raw_input('press enter to close..')
# ########################
